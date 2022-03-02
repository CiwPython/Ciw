import unittest
import ciw

class TimeDependentBatches(ciw.dists.Distribution):
    def sample(self, t, ind=None):
        if t < 11.0:
            return 5
        return 1

class TestArrivalNode(unittest.TestCase):
    def test_init_method(self):
        ciw.seed(5)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        N = ciw.ArrivalNode(Q)
        N.initialise()
        self.assertEqual(round(N.next_event_date, 5), 0.00440)
        self.assertEqual(N.number_of_individuals, 0)
        self.assertEqual(N.number_of_individuals_per_class, [0, 0, 0])
        self.assertEqual(N.number_accepted_individuals, 0)
        self.assertEqual(N.number_accepted_individuals_per_class, [0, 0, 0])
        dates_dict = {1: {0: 0.2110410999, 1: 0.1415614623, 2: 0.3923690877},
                      2: {0: 0.1218825551, 1: 0.0044003133, 2: 0.2442775601},
                      3: {0: 0.0819463473, 1: 0.4135097542, 2: 0.7256307839},
                      4: {0: 0.1738823223, 1: 0.3988184145, 2: 0.2987813628}}
        self.assertEqual({nd: {obs: round(N.event_dates_dict[nd][obs], 10)
            for obs in N.event_dates_dict[nd]} for nd in N.event_dates_dict},
            dates_dict)
