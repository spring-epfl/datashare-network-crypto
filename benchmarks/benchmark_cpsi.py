#!/usr/bin/env python3

import sys
import random
import time
import string
import json

sys.path.append('./')
sys.path.append('..')
from mspsi.cpsi import CPSIClient, CPSIServer

PUBLISHED_LIST = (10, 100, 1000, 10000, 100000)
QUERY_LIST = (1, 5, 10, 20)

class BenchmarkCPSI:
    def __init__(self, data, number_kwds_published, number_kwds_per_query, curve=415, repetitions=100, repetitions_publish=10):
        random.seed(0)

        self.data = data

        self.repetitions = repetitions
        self.repetitions_publish = repetitions_publish
        self.number_kwds_published = number_kwds_published
        self.number_kwds_per_query = number_kwds_per_query

        self.kwds_published = [(''.join((random.choice(string.ascii_lowercase) for _ in range(8)))) for _ in range(number_kwds_published)]
        self.kwds_query = [[(''.join((random.choice(string.ascii_lowercase) for _ in range(8)))) for _ in range(number_kwds_per_query)] for _ in range(repetitions)]

        self.cpsi_client = CPSIClient(curve)
        self.cpsi_server = CPSIServer(curve)

    def publish(self):
        kwds_published = [[(''.join((random.choice(string.ascii_lowercase) for _ in range(8)))) for _ in range(self.number_kwds_published)] for _ in range(self.repetitions_publish)]

        times = []
        for kwds in kwds_published:
            t0 = time.process_time()
            _ = self.cpsi_server.publish(kwds)
            t1 = time.process_time()

            times.append(t1-t0)

        self.data['publish'][self.number_kwds_published][0] = times

    def run(self):
        server_secret, published = self.cpsi_server.publish(self.kwds_published)

        times = []
        queries = []
        secrets = []
        for kwds in self.kwds_query:
            t0 = time.process_time()
            secret, query = self.cpsi_client.query(kwds)
            t1 = time.process_time()

            times.append(t1-t0)
            queries.append(query)
            secrets.append(secret)

        self.data['query'][self.number_kwds_published][self.number_kwds_per_query] = times

        times = []
        replies = []
        for query in queries:
            t0 = time.process_time()
            reply = self.cpsi_server.reply(server_secret, query)
            t1 = time.process_time()

            times.append(t1-t0)
            replies.append(reply)

        self.data['reply'][self.number_kwds_published][self.number_kwds_per_query] = times

        times = []
        for secret, reply in zip(secrets, replies):
            t0 = time.process_time()
            self.cpsi_client.compute_cardinality(secret, reply, published)
            t1 = time.process_time()

            times.append(t1-t0)

        self.data['cardinality'][self.number_kwds_published][self.number_kwds_per_query] = times


def write_data(filename, data):
    structure = {}
    for op in data.keys():
        elem = []
        for p in data[op].keys():
            for q in data[op][p].keys():
                times = {
                    'n_kwd_published': p,
                    'n_kwd_per_query': q,
                    'times' : data[op][p][q]
                }
                elem.append(times)
        structure[op] = elem

    content = json.dumps(structure)

    with open(filename, 'w') as fd:
        fd.write(content)

if __name__ == '__main__':
    data = {'publish': {}, 'query': {}, 'reply': {}, 'cardinality': {}}

    for n_kwds_published in PUBLISHED_LIST:
        for op in data.keys():
            data[op][n_kwds_published] = {}

        BenchmarkCPSI(data, n_kwds_published, 0).publish()
        for n_kwds_per_query in QUERY_LIST:
            BenchmarkCPSI(data, n_kwds_published, n_kwds_per_query).run()

    write_data('benchmark-cpsi.json', data)
