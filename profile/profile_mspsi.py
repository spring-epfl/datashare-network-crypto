import random
import string
import cProfile

from mspsi.mspsi import MSPSIClient, MSPSIServer

random.seed(0)

NUM_QUERIES = 1000
NUM_DOCS = 1000
CURVE = 415

def main():
    """Entry point of the program."""

    kwds_query = [[(''.join((random.choice(string.ascii_lowercase) for _ in range(16)))) for _ in range(10)] for _ in range(NUM_QUERIES)]
    docs_published = [[(''.join((random.choice(string.ascii_lowercase) for _ in range(16)))) for _ in range(100)] for _ in range(NUM_DOCS)]

    mspsi_client = MSPSIClient(CURVE)
    mspsi_server = MSPSIServer(CURVE)

    # Profile for publish()
    pr = cProfile.Profile()
    pr.enable()

    (secret_server, published) = mspsi_server.publish(docs_published)

    pr.disable()
    pr.print_stats()

    queries = []

    # Profile for query()
    pr = cProfile.Profile()
    pr.enable()

    for i in range(NUM_QUERIES):
        queries.append(mspsi_client.query(kwds_query[i]))

    pr.disable()
    pr.print_stats()

    replies = []

    # Profile for reply()
    pr = cProfile.Profile()
    pr.enable()

    for i in range(NUM_QUERIES):
        replies.append(mspsi_server.reply(secret_server, queries[i][1]))

    pr.disable()
    pr.print_stats()

    # Profile for compute_cardinalities()
    pr = cProfile.Profile()
    pr.enable()

    for i in range(NUM_QUERIES):
        mspsi_client.compute_cardinalities(queries[i][0], replies[i], published)

    pr.disable()
    pr.print_stats()

if __name__ == "__main__":
    main()
