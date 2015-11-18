import unittest
import asq

class TestExitNode(unittest.TestCase):

    def test_init_method(self):
        n = asq.ExitNode(100)
        self.assertEqual(n.id_number, -1)
        self.assertEqual(n.individuals, [])
        self.assertEqual(n.next_event_date, 100)
        self.assertEqual(n.node_capacity, 'Inf')

        n = asq.ExitNode('Inf')
        self.assertEqual(n.id_number, -1)
        self.assertEqual(n.individuals, [])
        self.assertEqual(n.next_event_date, 'Inf')
        self.assertEqual(n.node_capacity, 'Inf')



    def test_repr_method(self):
        n = asq.ExitNode(500)
        self.assertEqual(str(n), 'Exit Node')

        n = asq.ExitNode(2500)
        self.assertEqual(str(n), 'Exit Node')


    def test_accept_method(self):
        n = asq.ExitNode(200)
        i1 = asq.Individual(3)
        i2 = asq.Individual(8)
        self.assertEqual(n.individuals, [])
        n.accept(i1, 42.1)
        self.assertEqual(n.individuals, [i1])
        n.accept(i2, 51.8)
        self.assertEqual(n.individuals, [i1, i2])

    def test_update_next_event_date_method(self):
        n = asq.ExitNode(100)
        self.assertEqual(n.id_number, -1)
        self.assertEqual(n.individuals, [])
        self.assertEqual(n.next_event_date, 100)
        self.assertEqual(n.node_capacity, 'Inf')

        n.update_next_event_date()

        self.assertEqual(n.id_number, -1)
        self.assertEqual(n.individuals, [])
        self.assertEqual(n.next_event_date, 100)
        self.assertEqual(n.node_capacity, 'Inf')

