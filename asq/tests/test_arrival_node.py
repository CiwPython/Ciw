import unittest
import asq
from random import seed

class TestArrivalNode(unittest.TestCase):

    def test_init_method(self):
        seed(5)
        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        N = asq.ArrivalNode(Q)
        self.assertEqual(round(N.next_event_date, 5), 0.00440)
        self.assertEqual(N.number_of_individuals, 0)
        dates_dict = {1: {0: 0.21104109989445083, 1: 0.14156146233571273, 2: 0.3923690877168693}, 2: {0: 0.12188255510498336, 1: 0.004400313282484739, 2: 0.24427756009692883}, 3: {0: 0.08194634729677806, 1: 0.41350975417151004, 2: 0.7256307838738146}, 4: {0: 0.17388232234898224, 1: 0.39881841448612376, 2: 0.2987813628296875}}
        self.assertEqual(N.next_event_dates_dict, dates_dict)

    def test_initialise_next_event_dates_dict_method(self):
        seed(6)
        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        N = asq.ArrivalNode(Q)
        dates_dict_1 = {1: {0: 0.43622825409205973, 1: 0.26722324060759933, 2: 0.38642562730637603}, 2: {0: 0.16369523112791148, 1: 0.07147095652645417, 2: 0.8065738413825493}, 3: {0: 0.4088480189803173, 1: 0.0514323247956018, 2: 0.8132038176069183}, 4: {0: 1.157375143843249, 1: 0.46492767142177205, 2: 0.8176876726520277}}
        dates_dict_2 = {1: {0: 0.03258707753070194, 1: 0.8054262557674572, 2: 0.8168179514964325}, 2: {0: 0.08416713808943652, 1: 0.03282452990969279, 2: 0.219602384651059}, 3: {0: 0.25190890679024003, 1: 0.05735978139796031, 2: 1.5117882120904502}, 4: {0: 0.8881158889281887, 1: 0.05605926220383697, 2: 2.1307650867721044}}
        self.assertEqual(N.next_event_dates_dict, dates_dict_1)
        N.initialise_next_event_dates_dict()
        self.assertEqual(N.next_event_dates_dict, dates_dict_2)

    def test_repr_method(self):
        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        N = asq.ArrivalNode(Q)
        self.assertEqual(str(N), 'Arrival Node')

    def test_find_next_event_date_method(self):
        seed(1)
        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        N = asq.ArrivalNode(Q)
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
        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        N = asq.ArrivalNode(Q)
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
        Q = asq.Simulation(asq.load_parameters('tests/datafortesting/logs_test_for_simulation/'))
        N = asq.ArrivalNode(Q)
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


