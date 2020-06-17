#!/usr/bin/env python3

import sys
import random
import time
import datetime
import string
import json

sys.path.append('./')
sys.path.append('..')
from mspsi.mspsi import MSPSIClient, MSPSIServer

KEYWORD_LENGTH = 16
DEFAULT_CURVE = 415

PUBLISHED_DOCS_LIST = [ int(10**(i / 3)) for i in range(3, 13)]
PUBLISHED_KWDS_LIST = (100,)
QUERY_LIST = (10,)


class BenchmarkMSPSI:
    def __init__(self, data, number_docs_published, number_kwds_per_doc, number_kwds_per_query, curve=DEFAULT_CURVE, repetitions=10, repetitions_publish=5):
        random.seed(0)

        self.data = data

        self.repetitions = repetitions
        self.repetitions_publish = repetitions_publish
        self.number_docs_published = number_docs_published
        self.number_kwds_per_doc = number_kwds_per_doc
        self.number_kwds_per_query = number_kwds_per_query

        self.kwds_published = [[(''.join((random.choice(string.ascii_lowercase) for _ in range(KEYWORD_LENGTH)))) for _ in range(number_kwds_per_doc)] for _ in range(number_docs_published)]
        self.kwds_query = [[(''.join((random.choice(string.ascii_lowercase) for _ in range(KEYWORD_LENGTH)))) for _ in range(number_kwds_per_query)] for _ in range(repetitions)]

        self.mspsi_client = MSPSIClient(curve)
        self.mspsi_server = MSPSIServer(curve)


    def publish(self):
        docs_published = [[[(''.join((random.choice(string.ascii_lowercase) for _ in range(KEYWORD_LENGTH)))) for _ in range(self.number_kwds_per_doc)] for _ in range(self.number_docs_published)] for _ in range(self.repetitions_publish)]

        times = []
        lengths = []
        for docs in docs_published:
            t0 = time.process_time()
            # The seacret is not releveant for this benchmark.
            _, published = self.mspsi_server.publish(docs)
            t1 = time.process_time()

            length = MSPSIServer.published_len(published)

            times.append(t1-t0)
            lengths.append(length)

        self.data['publish'][self.number_docs_published][self.number_kwds_per_doc][0] = {'time': times, 'length': lengths}


    def run(self):
        (secret_server, published) = self.mspsi_server.publish(self.kwds_published)

        times = []
        lengths = []
        queries = []
        for kwds in self.kwds_query:
            t0 = time.process_time()
            query = self.mspsi_client.query(kwds)
            t1 = time.process_time()

            times.append(t1-t0)

            length = sum(map(lambda x: len(x), query[1]))
            lengths.append(length)

            queries.append(query)

        self.data['query'][self.number_docs_published][self.number_kwds_per_doc][self.number_kwds_per_query] = {'time': times, 'length': lengths}

        times = []
        lengths = []
        replies = []
        for query in queries:
            t0 = time.process_time()
            reply = self.mspsi_server.reply(secret_server, query[1])
            t1 = time.process_time()

            length = sum(map(lambda x: len(x), reply))

            times.append(t1-t0)
            lengths.append(length)
            replies.append(reply)

        self.data['reply'][self.number_docs_published][self.number_kwds_per_doc][self.number_kwds_per_query] = {'time': times, 'length': lengths}

        times = []
        for i, reply in enumerate(replies):
            t0 = time.process_time()
            self.mspsi_client.compute_cardinalities(queries[i][0], reply, published)
            t1 = time.process_time()

            times.append(t1-t0)
            # Computing lengths meaningless for cardinalities. This data is not transferred.

        self.data['cardinality'][self.number_docs_published][self.number_kwds_per_doc][self.number_kwds_per_query] = {'time': times, 'length':[]}


def write_data(filename, data):
    structure = {}
    for op in data.keys():
        elem = []
        for d in data[op].keys():
            for p in data[op][d].keys():
                for q in data[op][d][p].keys():
                    times = {
                        'n_document_published': d,
                        'n_kwd_per_doc': p,
                        'n_kwd_per_query': q,
                        'times' : data[op][d][p][q]['time'],
                        'lengths' : data[op][d][p][q]['length']
                    }
                    elem.append(times)
        structure[op] = elem

    content = json.dumps(structure)


    with open(filename, 'w') as fd:
        fd.write(content)


if __name__ == '__main__':
    data = {'publish': {}, 'query': {}, 'reply': {}, 'cardinality': {}}

    for n_docs_published in PUBLISHED_DOCS_LIST:
        for op in data.keys():
            data[op][n_docs_published] = {}
            for n_kwds_per_doc in PUBLISHED_KWDS_LIST:
                data[op][n_docs_published][n_kwds_per_doc] = {}

    for n_docs_published in PUBLISHED_DOCS_LIST:
        for n_kwds_per_doc in PUBLISHED_KWDS_LIST:
            print("Benchmarking #docs = {}, #kwds_per_doc = {}".format(n_docs_published, n_kwds_per_doc))
            for n_kwds_per_query in QUERY_LIST:
                BenchmarkMSPSI(data, n_docs_published, n_kwds_per_doc, n_kwds_per_query, curve=DEFAULT_CURVE).run()

    date = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%s')
    write_data('benchmark-mspsi-{}.json'.format(date), data)
