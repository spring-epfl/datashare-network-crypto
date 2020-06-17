#import sys
import unittest

#sys.path.append('../')
from mspsi.cpsi import CPSIClient, CPSIServer
from petlib.bn import Bn


class TestCPSI(unittest.TestCase):
    def __init__(self, tests):
        curve = 415
        self.cpsi_client = CPSIClient(curve)
        self.cpsi_server = CPSIServer(curve)
        super().__init__(tests)

    def test_all(self):
        kwds = ['foo', 'bar', '']
        server_secret, published = self.cpsi_server.publish(kwds)

        # Case where 2 keywords matches.
        client_secret, query = self.cpsi_client.query(['foo', ''])
        reply = self.cpsi_server.reply(server_secret, query)
        card = self.cpsi_client.compute_cardinality(client_secret, reply, published)

        self.assertEqual(card, 2)

        # Case where only 1 keyword matches.
        client_secret, query = self.cpsi_client.query(['bar', 'baz'])
        reply = self.cpsi_server.reply(server_secret, query)
        card = self.cpsi_client.compute_cardinality(client_secret, reply, published)

        self.assertEqual(card, 1)

        # Case where no keywords matches.
        client_secret, query = self.cpsi_client.query(['asdf', 'ghjk'])
        reply = self.cpsi_server.reply(server_secret, query)
        card = self.cpsi_client.compute_cardinality(client_secret, reply, published)

        self.assertEqual(card, 0)


if __name__ == '__main__':
    unittest.main()
