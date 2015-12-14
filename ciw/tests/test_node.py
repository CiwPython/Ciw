import unittest
import ciw
from random import seed

class TestNode(unittest.TestCase):

    def test_init_method(self):
        Q = ciw.Simulation(ciw.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        N = ciw.Node(1, Q)
        self.assertEqual(N.mu, [['Exponential', 7.0], ['Exponential', 7.0], ['Deterministic', 0.3]])
        self.assertEqual(N.c, 9)
        self.assertEqual(N.transition_row, [[0.1, 0.2, 0.1, 0.4], [0.6, 0.0, 0.0, 0.2], [0.0, 0.0, 0.4, 0.3]])
        self.assertEqual(N.next_event_date, 'Inf')
        self.assertEqual(N.individuals, [])
        self.assertEqual(N.id_number, 1)
        self.assertEqual([[round(obs, 1) for obs in row] for row in N.cum_transition_row], [[0.1, 0.3, 0.4, 0.8], [0.6, 0.6, 0.6, 0.8], [0.0, 0.0, 0.4, 0.7]])

        Q = ciw.Simulation(ciw.load_parameters('tests/datafortesting/logs_test_for_dynamic_classes/'))
        N1 = Q.transitive_nodes[0]
        self.assertEqual(N1.class_change_for_node, [[0.7, 0.3], [0.2, 0.8]])
        N2 = Q.transitive_nodes[1]
        self.assertEqual(N2.class_change_for_node, [[1.0, 0.0], [0.0, 1.0]])
       
        Q = ciw.Simulation(ciw.load_parameters('tests/datafortesting/logs_test_for_server_schedule/'))
        N = Q.transitive_nodes[0]
        self.assertEqual(N.scheduled_servers, True)
        self.assertEqual(N.cyclelength, 100)
        self.assertEqual(N.c, 1)
        self.assertEqual(N.masterschedule, [30, 60, 90, 100, 130, 160, 190, 200, 230, 260, 290])
        self.assertEqual(N.next_event_date, 30)

    def test_find_cdf_class_changes_method(self):
        Q = ciw.Simulation(ciw.load_parameters('tests/datafortesting/logs_test_for_dynamic_classes/'))
        N1 = Q.transitive_nodes[0]
        self.assertEqual(N1.find_cdf_class_changes(), [[0.7, 1.0], [0.2, 1.0]])

    def test_find_cum_transition_row_method(self):
        Q = ciw.Simulation(ciw.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        N = ciw.Node(1, Q)
        self.assertEqual([[round(obs, 1) for obs in row] for row in N.find_cum_transition_row()], [[0.1, 0.3, 0.4, 0.8], [0.6, 0.6, 0.6, 0.8], [0.0, 0.0, 0.4, 0.7]])

    def test_repr_method(self):
        Q = ciw.Simulation(ciw.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        N1 = ciw.Node(1, Q)
        N2 = ciw.Node(2, Q)
        self.assertEqual(str(N1), 'Node 1')
        self.assertEqual(str(N2), 'Node 2')

    def test_change_shift_method(self):
        Q = ciw.Simulation(ciw.load_parameters('tests/datafortesting/logs_test_for_server_schedule/'))
        N = Q.transitive_nodes[0]
        N.next_event_date = 30
        self.assertEqual([str(obs) for obs in N.servers], ['Server 1 at Node 1'])
        self.assertEqual([obs.busy for obs in N.servers], [False])
        self.assertEqual([obs.offduty for obs in N.servers], [False])
        self.assertEqual(N.c, 1)
        N.change_shift()
        self.assertEqual([str(obs) for obs in N.servers], ['Server 2 at Node 1', 'Server 3 at Node 1'])
        self.assertEqual([obs.busy for obs in N.servers], [False, False])
        self.assertEqual([obs.offduty for obs in N.servers], [False, False])
        self.assertEqual(N.c, 2)

        N.servers[0].busy = True
        N.next_event_date = 90
        N.change_shift()
        self.assertEqual([str(obs) for obs in N.servers], ['Server 2 at Node 1', 'Server 4 at Node 1', 'Server 5 at Node 1', 'Server 6 at Node 1'])
        self.assertEqual([obs.busy for obs in N.servers], [True, False, False, False])
        self.assertEqual([obs.offduty for obs in N.servers], [True, False, False, False])
        self.assertEqual(N.c, 3)

