import random
import string
import sys
import unittest

from petlib.bn import Bn

#sys.path.append('../')
from mspsi.mspsi import MSPSIClient, MSPSIServer


class TestMSPSI(unittest.TestCase):
    def __init__(self, tests):
        curve = 415
        self.mspsi_client = MSPSIClient(curve)
        self.mspsi_server = MSPSIServer(curve)
        super().__init__(tests)

    def test_functionality(self):
        kwds = [['foo', 'bar', ''], ['foo', 'baz'], ['asdf']]
        (secret_server, published) = self.mspsi_server.publish(kwds)

        # Case where respectively 2, 1 and no keywords matches.
        (secret_client, query) = self.mspsi_client.query(['foo', ''])
        reply = self.mspsi_server.reply(secret_server, query)
        cards = self.mspsi_client.compute_cardinalities(secret_client, reply, published)

        for i, j in zip(cards, [2, 1, 0]):
            self.assertEqual(i, j)

        # Case where respectively 1, 1 and no keywords matches.
        (secret_client, query) = self.mspsi_client.query(['bar', 'baz'])
        reply = self.mspsi_server.reply(secret_server, query)
        cards = self.mspsi_client.compute_cardinalities(secret_client, reply, published)

        for i, j in zip(cards, [1, 1, 0]):
            self.assertEqual(i, j)

        # Case where respectively 0, 0 and 1 keywords matches.
        (secret_client, query) = self.mspsi_client.query(['asdf', 'ghjk'])
        reply = self.mspsi_server.reply(secret_server, query)
        cards = self.mspsi_client.compute_cardinalities(secret_client, reply, published)

        for i, j in zip(cards, [0, 0, 1]):
            self.assertEqual(i, j)

    def test_false_positives(self):
        # Random data generation with keywords known to be inside the corpus
        random.seed(0)

        # sets of documents are generated.
        kwds_in_doc_and_in_query = set([''.join([random.choice(string.ascii_lowercase) for _ in range(16)]) for _ in range(20)])
        kwds_in_doc_not_in_query = set([''.join([random.choice(string.ascii_lowercase) for _ in range(16)]) for _ in range(1000)])
        kwds_not_in_doc_in_query = set([''.join([random.choice(string.ascii_lowercase) for _ in range(16)]) for _ in range(1000)])

        # Ensure there ate no intersection between these two sets.
        kwds_in_doc_not_in_query -= kwds_in_doc_and_in_query

        # Ensure there ate no intersection between this set and the two others.
        kwds_not_in_doc_in_query -= kwds_in_doc_and_in_query
        kwds_not_in_doc_in_query -= kwds_in_doc_not_in_query

        kwds_in_doc_and_in_query = list(kwds_in_doc_and_in_query)
        kwds_in_doc_not_in_query = list(kwds_in_doc_not_in_query)
        kwds_not_in_doc_in_query = list(kwds_not_in_doc_in_query)

        # generate documents
        docs = [kwds_in_doc_and_in_query + [random.choice(kwds_in_doc_not_in_query) for _ in range(100)] for _ in range(1000)]

        # generates queries content.
        queries_full = [[random.choice(kwds_in_doc_and_in_query) for _ in range(10)] for _ in range(1000)]
        queries_none = [[random.choice(kwds_not_in_doc_in_query) for _ in range(10)] for _ in range(1000)]
        queries_50 = [([random.choice(kwds_in_doc_and_in_query) for _ in range(5)] + [random.choice(kwds_not_in_doc_in_query) for _ in range(5)]) for _ in range(1000)]

        # Publication of the documents
        (secret_server, published) = self.mspsi_server.publish(docs)

        err_false_neg = 0
        err_false_pos = 0
        n_matches = 0

        for queries, expected, info_str in zip((queries_full, queries_50, queries_none), ([10] * 10, [5] * 10, [0] * 10), ('\n===== Full Match =====', '\n===== 50% match ======', '\n===== 0% match =======')):
            print(info_str)
            for query in queries:
                n_matches += 1

                (secret_client, query) = self.mspsi_client.query(query)
                reply = self.mspsi_server.reply(secret_server, query)
                cards = self.mspsi_client.compute_cardinalities(secret_client, reply, published)

                for i, j in zip(cards, expected):
                    if i != j:
                        if i > j:
                            n_false = i - j
                            print('{} false positive found (expected: {}, found: {})'.format(n_false, j, i))
                            err_false_pos += n_false
                        else:
                            n_false = j - i
                            print('{} false negatives found (expected: {}, found: {})'.format(n_false, j, i))
                            err_false_neg += n_false

        print('A total of {} false negative and {} false positive were for {} queries of 10 keywords.'.format(err_false_neg, err_false_pos, n_matches))


if __name__ == '__main__':
    unittest.main()
