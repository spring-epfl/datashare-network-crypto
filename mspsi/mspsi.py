"""
Multi set PSI
"""

from hashlib import blake2b
from typing import List, Tuple

from petlib.bn import Bn
from petlib.ec import EcGroup, EcPt

from cuckoopy_mod import CuckooFilter


CUCKOO_FILTER_CAPACITY_MIN = 1000
CUCKOO_FILTER_CAPACITY_FRACTION = 0.3
CUCKOO_FILTER_BUCKET_SIZE = 6
CUCKOO_FILTER_FINGERPRINT_SIZE = 4
DOC_ID_SIZE = 4
EC_NID_DEFAULT = 415
ENCODING_DEFAULT = "utf-8"


def kwd_encode(doc_id:bytes, kwd:bytes) -> bytes:
    """
    Hash an encrypted keyword and its doc id.
    :param doc_id: id of the document
    :param kwd: an encrypted keyword of the document
    :return: a cryptographically secure hash as a binary string
    """
    return blake2b(doc_id + kwd).digest()


class MSPSIClient:
    """
    Client for a multi set PSI
    """

    def __init__(self, curve:int=EC_NID_DEFAULT):
        """
        Constructor for the client of a multi set PSI

        :param curve: NID of the elliptic curve to use
        """

        self.group = EcGroup(curve)


    def query(self, kwds:List[str]) -> Tuple[Bn, List[bytes]]:
        """
        Generate a query from the keywords.

        :param kwds_ms: Multi set of keywords to be queried
        :return: a secret to generate the query and the query itself
        """

        secret = self.group.order().random()

        query_enc = list()

        for kwd in kwds:
            kwd_pt = self.group.hash_to_point(kwd.encode(ENCODING_DEFAULT))
            kwd_enc = secret * kwd_pt
            kwd_enc_bytes = kwd_enc.export()
            query_enc.append(kwd_enc_bytes)

        return (secret, query_enc)


    def compute_cardinalities(self, secret:Bn, reply:List[bytes], published:Tuple[int, CuckooFilter]) -> List[int]:
        """
        Compute the cardinalyty of the intersection of sets between the reply to a query
        and the list of lists of points published by the server.

        :param secret: secret with which the query was encrypted
        :param reply: reply from the server
        :param published: list of lists of point published by the server
        :return: list of cardinalities for the intersection between the reply and each published list of points.
        """

        n_docs = published[0]
        published_data = published[1]
        secret_inv = secret.mod_inverse(self.group.order())
        cardinalities = []

        # For optimisation the following assumptions are made
        # - all keywords in the query are different.
        # - all keywords in the document are different.
        kwds_dec = list()

        for kwd_h in reply:
            kwd_pt = EcPt.from_binary(kwd_h, self.group)
            kwd_pt_dec = secret_inv * kwd_pt
            kwd_bytes = kwd_pt_dec.export()
            kwds_dec.append(kwd_bytes)

        for doc_id in range(n_docs):
            n_matches = 0
            encoded_doc_id = doc_id.to_bytes(DOC_ID_SIZE, byteorder="big")
            for kwd_dec in kwds_dec:
                kwd_docid_bytes = kwd_encode(encoded_doc_id, kwd_dec)
                if published_data.contains(kwd_docid_bytes):
                    n_matches += 1
            cardinalities.append(n_matches)

        return cardinalities



class MSPSIServer:
    """
    Server for a multi set PSI
    """

    def __init__(self, curve:int=EC_NID_DEFAULT):
        """
        Constructor for the server of a multi set PSI

        :param curve: NID of the elliptic curve to use.
        """

        self.group = EcGroup(curve)


    @staticmethod
    def published_len(published:CuckooFilter) -> int:
        """
        Compute the size of a given published data.
        :param published: published data
        """
        published_data = published[1]
        capacity = published_data.capacity
        bucket_size = published_data.bucket_size
        return capacity * bucket_size


    def publish(self, docs:List[List[str]]) -> Tuple[Bn, Tuple[int, CuckooFilter]]:
        """
        Generate a list of lists of points on the EC corresponding to a document's keywords.

        :param docs: a list of list of keywords for each document.
        :return: a secret with wich the keywords were encrypted and a cuckoo filter containing the encrypted keywords.
        """

        cuckoo_capacity = 0
        for kwds in docs:
            cuckoo_capacity += len(kwds)

        cuckoo_capacity *= CUCKOO_FILTER_CAPACITY_FRACTION

        # Ensure some minimal capacity on filter
        cuckoo_capacity = max(CUCKOO_FILTER_CAPACITY_MIN, int(cuckoo_capacity))

        secret = self.group.order().random()

        pub = CuckooFilter(
            capacity=cuckoo_capacity,
            bucket_size=CUCKOO_FILTER_BUCKET_SIZE,
            fingerprint_size=CUCKOO_FILTER_FINGERPRINT_SIZE
        )

        for doc_id, kwds in enumerate(docs):
            encoded_doc_id = doc_id.to_bytes(DOC_ID_SIZE, byteorder="big")
            for kwd in kwds:
                kwd_pt = self.group.hash_to_point(kwd.encode(ENCODING_DEFAULT))
                kwd_enc = secret * kwd_pt
                kwd_enc_bytes = kwd_enc.export()
                kwd_docid_bytes = kwd_encode(encoded_doc_id, kwd_enc_bytes)
                pub.insert(kwd_docid_bytes)

        return (secret, (len(docs), pub))


    def reply(self, secret:Bn, query:List[bytes]) -> List[Bn]:
        """
        Compute a reply to a query.

        :param secret: secret with which the keywords were encrypted during the publication
        :param query: query to be answered
        :return: reply to the query
        """

        reply = list()

        for kwd_h in query:
            kwd_pt = EcPt.from_binary(kwd_h, self.group)
            kwd_enc = secret * kwd_pt
            kwd_enc_bytes = kwd_enc.export()
            reply.append(kwd_enc_bytes)

        return reply
