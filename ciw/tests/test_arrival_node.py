import unittest
import ciw
from random import seed

class TestArrivalNode(unittest.TestCase):

    def test_init_method(self):
        seed(5)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        N = ciw.ArrivalNode(Q)
        self.assertEqual(round(N.next_event_date, 5), 0.00440)
        self.assertEqual(N.number_of_individuals, 0)
        dates_dict = {1: {0: 0.2110410999, 1: 0.1415614623, 2: 0.3923690877}, 2: {0: 0.1218825551, 1: 0.0044003133, 2: 0.2442775601}, 3: {0: 0.0819463473, 1: 0.4135097542, 2: 0.7256307839}, 4: {0: 0.1738823223, 1: 0.3988184145, 2: 0.2987813628}}
        self.assertEqual({nd:{obs:round(N.next_event_dates_dict[nd][obs], 10) for obs in N.next_event_dates_dict[nd]} for nd in N.next_event_dates_dict}, dates_dict)

    def test_initialise_next_event_dates_dict_method(self):
        seed(6)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        N = ciw.ArrivalNode(Q)
        dates_dict_1 = {1: {0: 0.4362282541, 1: 0.2672232406, 2: 0.3864256273}, 2: {0: 0.1636952311, 1: 0.0714709565, 2: 0.8065738414}, 3: {0: 0.4088480190, 1: 0.0514323248, 2: 0.8132038176}, 4: {0: 1.1573751438, 1: 0.4649276714, 2: 0.8176876727}}
        dates_dict_2 = {1: {0: 0.0325870775, 1: 0.8054262558, 2: 0.8168179515}, 2: {0: 0.0841671381, 1: 0.0328245299, 2: 0.2196023847}, 3: {0: 0.2519089068, 1: 0.0573597814, 2: 1.5117882121}, 4: {0: 0.8881158889, 1: 0.0560592622, 2: 2.1307650868}}
        self.assertEqual({nd:{obs:round(N.next_event_dates_dict[nd][obs], 10) for obs in N.next_event_dates_dict[nd]} for nd in N.next_event_dates_dict}, dates_dict_1)
        N.initialise_next_event_dates_dict()
        self.assertEqual({nd:{obs:round(N.next_event_dates_dict[nd][obs], 10) for obs in N.next_event_dates_dict[nd]} for nd in N.next_event_dates_dict}, dates_dict_2)

    def test_repr_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        N = ciw.ArrivalNode(Q)
        self.assertEqual(str(N), 'Arrival Node')

    def test_find_next_event_date_method(self):
        seed(1)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        N = ciw.ArrivalNode(Q)
        self.assertEqual(round(N.next_event_date, 5), 0.00105)
        N.find_next_event_date()
        self.assertEqual(round(N.next_event_date, 5), 0.00105)
        self.assertEqual(N.next_node, 1)
        self.assertEqual(N.next_class, 1)

        N.have_event()
        self.assertEqual(round(N.next_event_date, 5), 0.00518)
        self.assertEqual(N.next_node, 3)
        self.assertEqual(N.next_class, 1)

    def test_have_event_method(self):
        seed(1)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        N = ciw.ArrivalNode(Q)
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[0].individuals], [])
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[1].individuals], [])
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[2].individuals], [])
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[3].individuals], [])
        self.assertEqual(round(N.next_event_date, 5), 0.00105)
        self.assertEqual(N.next_node, 1)

        N.have_event()
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[0].individuals], ['Individual 1'])
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[1].individuals], [])
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[2].individuals], [])
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[3].individuals], [])
        self.assertEqual(round(N.next_event_date, 5), 0.00518)
        self.assertEqual(N.next_node, 3)

        seed(12)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/'))
        N = ciw.ArrivalNode(Q)
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[0].individuals], [])
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[1].individuals], [])
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[2].individuals], [])
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[3].individuals], [])
        self.assertEqual(round(N.next_event_date, 5), 0.01938)
        self.assertEqual(N.next_node, 3)

        N.have_event()
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[0].individuals], [])
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[1].individuals], [])
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[2].individuals], ['Individual 1'])
        self.assertEqual([str(obj) for obj in Q.transitive_nodes[3].individuals], [])
        self.assertEqual(round(N.next_event_date, 5), 0.02021)
        self.assertEqual(N.next_node, 2)

    def test_no_arrivals_example(self):
        params = ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/')
        params['Arrival_rates']['Class 0'] = ['NoArrivals', ['Exponential', 1.0], ['Exponential', 4.0], ['Exponential', 3.5]]
        Q = ciw.Simulation(params)
        AN = Q.nodes[0]
        self.assertEqual(AN.simulation.lmbda[0][0], 'NoArrivals')
        self.assertEqual(AN.sample_next_event_time(1, 0), 'Inf')

