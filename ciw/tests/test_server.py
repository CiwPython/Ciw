import unittest
import ciw

class TestServer(unittest.TestCase):

    def test_init_method(self):
        Q = ciw.Simulation(ciw.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        N = Q.transitive_nodes[1]
        s = ciw.Server(N, 3)
        self.assertEqual(s.id_number, 3)
        self.assertEqual(s.node, N)
        self.assertEqual(s.node.id_number, 2)
        self.assertEqual(s.cust, False)
        self.assertEqual(s.busy, False)
        self.assertEqual(s.offduty, False)


    def test_repr_method(self):
        Q = ciw.Simulation(ciw.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        N = Q.transitive_nodes[0]
        s = ciw.Server(N, 4)
        self.assertEqual(str(s), 'Server 4 at Node 1')