"""
Single set PSI
"""

from typing import List, Tuple

from petlib.bn import Bn
from petlib.ec import EcGroup, EcPt


EC_NID_DEFAULT = 415
ENCODING_DEFAULT = "utf-8"


class CPSIClient:
    """
    Client for a single set PSI
    """

    def __init__(self, curve:int=EC_NID_DEFAULT):
        """
        Constructor for the client of a single set PSI

        :param curve: NID of the elliptic curve to use.
        """

        self.group = EcGroup(curve)


    def query(self, kwds:List[str]) -> Tuple[Bn, List[bytes]]:
        """
        Generate a query from the keywords.

        :param kwds_ms: Multi set of keywords to be queried.
        :return: a query
        """

        secret = self.group.order().random()

        query_enc = list()

        for kwd in kwds:
            kwd_pt = self.group.hash_to_point(kwd.encode(ENCODING_DEFAULT))
            kwd_enc = secret * kwd_pt
            kwd_enc_bytes = kwd_enc.export()
            query_enc.append(kwd_enc_bytes)

        return (secret, query_enc)


    def compute_cardinality(self, secret:Bn, reply:List[bytes], published) -> int:
        """
        Compute the cardinalyty of the intersection of sets between the reply to a query
        and the list of points published by the server.

        :param reply: reply from the server
        :param published: list of point published by the server
        :return: cardinalityof the intersection of sets
        """

        secret_inv = secret.mod_inverse(self.group.order())

        kwds = list()

        for kwd_h in reply:
            kwd_pt = EcPt.from_binary(kwd_h, self.group)
            kwd_pt_dec = secret_inv * kwd_pt
            kwd_bytes = kwd_pt_dec.export()
            kwds.append(kwd_bytes)

        # The intersection of the 2 sets is the number of matches.
        return len(set(kwds) & set(published))


class CPSIServer:
    """
    Server for a single set PSI
    """

    def __init__(self, curve:int=EC_NID_DEFAULT):
        """
        Constructor for the server of a single set PSI

        :param curve: NID of the elliptic curve to use.
        :return:
        """

        self.group = EcGroup(curve)


    def publish(self, kwds:List[str]) -> Tuple[Bn, List[bytes]]:
        """
        Generate a list of points on the EC corresponding to a document's keywords.

        :param kwds: list of keywords in the document.
        :return: a list of points on the EC corresponding to a document's keywords
        """

        secret = self.group.order().random()

        pub = list()

        for kwd in kwds:
            kwd_pt = self.group.hash_to_point(kwd.encode(ENCODING_DEFAULT))
            kwd_enc = secret * kwd_pt
            kwd_enc_bytes = kwd_enc.export()
            pub.append(kwd_enc_bytes)

        return (secret, pub)


    def reply(self, secret:Bn, query:List[bytes]) -> List[bytes]:
        """
        Compute a reply to a query.

        :param query: Query to be answered.
        :return: reply to the query
        """

        reply = list()

        for kwd_h in query:
            kwd_pt = EcPt.from_binary(kwd_h, self.group)
            kwd_enc = secret * kwd_pt
            kwd_enc_bytes = kwd_enc.export()
            reply.append(kwd_enc_bytes)

        return reply
