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
        self.assertEqual(round(N.next_event_date, 5), 0.00440)
        self.assertEqual(N.number_of_individuals, 0)
        dates_dict = {1: {0: 0.2110410999, 1: 0.1415614623, 2: 0.3923690877},
                      2: {0: 0.1218825551, 1: 0.0044003133, 2: 0.2442775601},
                      3: {0: 0.0819463473, 1: 0.4135097542, 2: 0.7256307839},
                      4: {0: 0.1738823223, 1: 0.3988184145, 2: 0.2987813628}}
        self.assertEqual({nd: {obs: round(N.event_dates_dict[nd][obs], 10)
            for obs in N.event_dates_dict[nd]} for nd in N.event_dates_dict},
            dates_dict)

    def test_initialise_event_dates_dict_method(self):
        ciw.seed(6)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        N = ciw.ArrivalNode(Q)
        dates_dict_1 = {1: {0: 0.4362282541, 1: 0.2672232406, 2: 0.3864256273},
                        2: {0: 0.1636952311, 1: 0.0714709565, 2: 0.8065738414},
                        3: {0: 0.4088480190, 1: 0.0514323248, 2: 0.8132038176},
                        4: {0: 1.1573751438, 1: 0.4649276714, 2: 0.8176876727}}
        dates_dict_2 = {1: {0: 0.0325870775, 1: 0.8054262558, 2: 0.8168179515},
                        2: {0: 0.0841671381, 1: 0.0328245299, 2: 0.2196023847},
                        3: {0: 0.2519089068, 1: 0.0573597814, 2: 1.5117882121},
                        4: {0: 0.8881158889, 1: 0.0560592622, 2: 2.1307650868}}
        self.assertEqual({nd: {obs: round(N.event_dates_dict[nd][obs], 10)
            for obs in N.event_dates_dict[nd]} for nd in N.event_dates_dict},
            dates_dict_1)
        N.initialise_event_dates_dict()
        self.assertEqual({nd: {obs: round(N.event_dates_dict[nd][obs], 10)
            for obs in N.event_dates_dict[nd]} for nd in N.event_dates_dict},
            dates_dict_2)

    def test_repr_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        N = ciw.ArrivalNode(Q)
        self.assertEqual(str(N), 'Arrival Node')

    def test_find_next_event_date_method(self):
        ciw.seed(1)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
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
        ciw.seed(1)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        N = ciw.ArrivalNode(Q)
        self.assertEqual(Q.transitive_nodes[0].all_individuals, [])
        self.assertEqual(Q.transitive_nodes[0].individuals, [[]])
        self.assertEqual(Q.transitive_nodes[1].all_individuals, [])
        self.assertEqual(Q.transitive_nodes[1].individuals, [[]])
        self.assertEqual(Q.transitive_nodes[2].all_individuals, [])
        self.assertEqual(Q.transitive_nodes[2].individuals, [[]])
        self.assertEqual(Q.transitive_nodes[3].all_individuals, [])
        self.assertEqual(Q.transitive_nodes[3].individuals, [[]])
        self.assertEqual(round(N.next_event_date, 5), 0.00105)
        self.assertEqual(N.next_node, 1)

        N.have_event()
        self.assertEqual([str(obj) for obj
            in Q.transitive_nodes[0].all_individuals],
            ['Individual 1'])
        self.assertEqual([str(obj) for pr_cls in
            Q.transitive_nodes[0].individuals  for obj in pr_cls],
            ['Individual 1'])
        self.assertEqual(Q.transitive_nodes[1].all_individuals, [])
        self.assertEqual(Q.transitive_nodes[1].individuals, [[]])
        self.assertEqual(Q.transitive_nodes[2].all_individuals, [])
        self.assertEqual(Q.transitive_nodes[2].individuals, [[]])
        self.assertEqual(Q.transitive_nodes[3].all_individuals, [])
        self.assertEqual(Q.transitive_nodes[3].individuals, [[]])
        self.assertEqual(round(N.next_event_date, 5), 0.00518)
        self.assertEqual(N.next_node, 3)

        ciw.seed(12)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        N = ciw.ArrivalNode(Q)
        self.assertEqual(Q.transitive_nodes[0].all_individuals, [])
        self.assertEqual(Q.transitive_nodes[0].individuals, [[]])
        self.assertEqual(Q.transitive_nodes[1].all_individuals, [])
        self.assertEqual(Q.transitive_nodes[1].individuals, [[]])
        self.assertEqual(Q.transitive_nodes[2].all_individuals, [])
        self.assertEqual(Q.transitive_nodes[2].individuals, [[]])
        self.assertEqual(Q.transitive_nodes[3].all_individuals, [])
        self.assertEqual(Q.transitive_nodes[3].individuals, [[]])
        self.assertEqual(round(N.next_event_date, 5), 0.01938)
        self.assertEqual(N.next_node, 3)

        N.have_event()
        self.assertEqual(Q.transitive_nodes[0].all_individuals, [])
        self.assertEqual(Q.transitive_nodes[0].individuals, [[]])
        self.assertEqual(Q.transitive_nodes[1].all_individuals, [])
        self.assertEqual(Q.transitive_nodes[1].individuals, [[]])
        self.assertEqual([str(obj) for obj
            in Q.transitive_nodes[2].all_individuals],
            ['Individual 1'])
        self.assertEqual([str(obj) for pr_cls
            in Q.transitive_nodes[2].individuals  for obj in pr_cls],
            ['Individual 1'])
        self.assertEqual(Q.transitive_nodes[3].all_individuals, [])
        self.assertEqual(Q.transitive_nodes[3].individuals, [[]])
        self.assertEqual(round(N.next_event_date, 5), 0.02021)
        self.assertEqual(N.next_node, 2)

    def test_no_arrivals_example(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.NoArrivals(), ciw.dists.Exponential(1)],
            service_distributions=[ciw.dists.Exponential(4), ciw.dists.Exponential(4)],
            routing=[[0.5, 0.1], [0.1, 0.1]],
            number_of_servers=[1, 2])
        Q = ciw.Simulation(N)
        AN = Q.nodes[0]
        self.assertEqual(
            str(AN.simulation.network.customer_classes[0].arrival_distributions[0]),
            'NoArrivals')
        self.assertEqual(AN.inter_arrival(1, 0), float('Inf'))

    def test_rejection_dict(self):
        params = {'arrival_distributions':[ciw.dists.Deterministic(3.0),
                                           ciw.dists.Deterministic(4.0)],
                  'service_distributions':[ciw.dists.Deterministic(10.0),
                                           ciw.dists.Deterministic(10.0)],
                  'routing':[[0.0, 1.0], [0.0, 0.0]],
                  'number_of_servers':[1, 1],
                  'queue_capacities':[1, 1]}
        Q = ciw.Simulation(ciw.create_network(**params))
        self.assertEqual(Q.rejection_dict, {1: {0: []}, 2: {0:[]}})
        Q.simulate_until_max_time(20)
        self.assertEqual(Q.rejection_dict,
            {1: {0: [9.0, 12.0, 18.0]}, 2: {0: [12.0, 16.0]}})

    def test_send_individual(self):
        params = {'arrival_distributions':[ciw.dists.Exponential(3.0)],
                  'service_distributions':[ciw.dists.Exponential(10.0)],
                  'routing':[[0.5]],
                  'number_of_servers':[1]}
        Q = ciw.Simulation(ciw.create_network(**params))
        AN = Q.nodes[0]
        ind1 = ciw.Individual(555)
        ind2 = ciw.Individual(666)
        self.assertEqual(Q.nodes[1].all_individuals, [])
        self.assertEqual(Q.nodes[1].individuals, [[]])
        AN.send_individual(Q.nodes[1], ind1)
        self.assertEqual(Q.nodes[1].all_individuals, [ind1])
        self.assertEqual(Q.nodes[1].individuals, [[ind1]])
        AN.send_individual(Q.nodes[1], ind2)
        self.assertEqual(Q.nodes[1].all_individuals, [ind1, ind2])
        self.assertEqual(Q.nodes[1].individuals, [[ind1, ind2]])

    def test_report_rejection(self):
        params = {'arrival_distributions':[ciw.dists.Exponential(3.0)],
                  'service_distributions':[ciw.dists.Exponential(10.0)],
                  'routing':[[0.5]],
                  'number_of_servers':[1]}
        Q = ciw.Simulation(ciw.create_network(**params))
        AN = Q.nodes[0]
        AN.next_event_date = 3.33
        self.assertEqual(AN.rejection_dict, {1: {0: []}})
        AN.record_rejection(Q.nodes[1])
        self.assertEqual(AN.rejection_dict, {1: {0: [3.33]}})
        AN.next_event_date = 4.44
        AN.record_rejection(Q.nodes[1])
        self.assertEqual(AN.rejection_dict, {1: {0: [3.33, 4.44]}})

    def test_update_next_event_date_passes(self):
        params = {'arrival_distributions':[ciw.dists.Exponential(3.0)],
                  'service_distributions':[ciw.dists.Exponential(10.0)],
                  'routing':[[0.5]],
                  'number_of_servers':[1]}
        Q = ciw.Simulation(ciw.create_network(**params))
        AN = Q.nodes[0]
        AN.next_event_date = 3.33
        AN.update_next_event_date()
        self.assertEqual(AN.next_event_date, 3.33)
        AN.update_next_event_date()
        self.assertEqual(AN.next_event_date, 3.33)

    def test_batching(self):
        # Test that 2 arrivals occur at a time
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([5.0, 5.0, 100.0])],
            service_distributions=[ciw.dists.Sequential([2.0, 3.0])],
            number_of_servers=[1],
            batching_distributions=[ciw.dists.Deterministic(2)]
        )
        Q = ciw.Simulation(N)
        N = Q.transitive_nodes[0]

        self.assertEqual(len(N.all_individuals), 0)
        Q.nodes[0].have_event()
        self.assertEqual(len(N.all_individuals), 2)
        Q.nodes[0].have_event()
        self.assertEqual(len(N.all_individuals), 4)
        Q.nodes[0].have_event()
        self.assertEqual(len(N.all_individuals), 6)

        # Test that batched individuals have same arrival date
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([5.0, 5.0, 2.0, 1.0, 5.0, 100.0])],
            service_distributions=[ciw.dists.Sequential([2.0, 3.0])],
            number_of_servers=[1],
            batching_distributions=[ciw.dists.Deterministic(2)]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(70.0)
        recs = Q.get_all_records()

        self.assertEqual(
            [r.arrival_date for r in recs],
            [5.0, 5.0, 10.0, 10.0, 12.0, 12.0, 13.0, 13.0, 18.0, 18.0])
        self.assertEqual(
            [r.service_start_date for r in recs],
            [5.0, 7.0, 10.0, 12.0, 15.0, 17.0, 20.0, 22.0, 25.0, 27.0])
        self.assertEqual(
            [r.service_time for r in recs],
            [2.0, 3.0, 2.0, 3.0, 2.0, 3.0, 2.0, 3.0, 2.0, 3.0])
        self.assertEqual(
            [r.service_end_date for r in recs],
            [7.0, 10.0, 12.0, 15.0, 17.0, 20.0, 22.0, 25.0, 27.0, 30.0])
        self.assertEqual(
            [r.waiting_time for r in recs],
            [0.0, 2.0, 0.0, 2.0, 3.0, 5.0, 7.0, 9.0, 7.0, 9.0])

    def test_batching_sequential(self):
        # Test sequential batches
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([5.0, 5.0, 100.0])],
            service_distributions=[ciw.dists.Sequential([2.0, 3.0])],
            number_of_servers=[1],
            batching_distributions=[ciw.dists.Sequential([1, 1, 4, 2, 1, 5])]
        )
        Q = ciw.Simulation(N)
        N = Q.transitive_nodes[0]

        self.assertEqual(len(N.all_individuals), 0)
        Q.nodes[0].have_event()
        self.assertEqual(len(N.all_individuals), 1)
        Q.nodes[0].have_event()
        self.assertEqual(len(N.all_individuals), 2)
        Q.nodes[0].have_event()
        self.assertEqual(len(N.all_individuals), 6)
        Q.nodes[0].have_event()
        self.assertEqual(len(N.all_individuals), 8)
        Q.nodes[0].have_event()
        self.assertEqual(len(N.all_individuals), 9)
        Q.nodes[0].have_event()
        self.assertEqual(len(N.all_individuals), 14)
        Q.nodes[0].have_event()
        self.assertEqual(len(N.all_individuals), 15)
        Q.nodes[0].have_event()
        self.assertEqual(len(N.all_individuals), 16)
        Q.nodes[0].have_event()
        self.assertEqual(len(N.all_individuals), 20)

    def test_batching_custom(self):
        # Test custom batches
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([5.0, 5.0, 100.0])],
            service_distributions=[ciw.dists.Sequential([2.0, 3.0])],
            number_of_servers=[1],
            batching_distributions=[ciw.dists.Pmf([1, 5], [0.5, 0.5])]
        )
        ciw.seed(12)
        Q = ciw.Simulation(N)
        N = Q.transitive_nodes[0]

        observerd_inds = []
        for _ in range(20):
            observerd_inds.append(len(N.all_individuals))
            Q.nodes[0].have_event()

        # Numbers of individuals should only increase by 1 or by 5
        self.assertEqual(observerd_inds,
            [0, 1, 6, 11, 12, 13, 14, 15, 20, 25, 30, 35, 40, 41, 42, 43, 48, 49, 54, 55])

    def test_batching_multi_node(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(20),
                                   ciw.dists.Deterministic(23),
                                   ciw.dists.Deterministic(25)],
            service_distributions=[ciw.dists.Deterministic(1),
                                   ciw.dists.Deterministic(1),
                                   ciw.dists.Deterministic(1)],
            number_of_servers=[10, 10, 10],
            batching_distributions=[ciw.dists.Deterministic(3),
                                    ciw.dists.Deterministic(2),
                                    ciw.dists.Deterministic(1)],
            routing=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        )
        ciw.seed(12)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(28)
        recs = Q.get_all_records()
        
        arrivals = [r.arrival_date for r in recs]
        nodes = [r.node for r in recs]
        classes = [r.customer_class for r in recs]
        self.assertEqual(arrivals, [20, 20, 20, 23, 23, 25])
        self.assertEqual(nodes, [1, 1, 1, 2, 2, 3])
        self.assertEqual(classes, [0, 0, 0, 0, 0, 0])

    def test_batching_multi_classes(self):
        N = ciw.create_network(
            arrival_distributions={'Class 0': [ciw.dists.Deterministic(20)],
                                   'Class 1': [ciw.dists.Deterministic(23)],
                                   'Class 2': [ciw.dists.Deterministic(25)]},
            service_distributions={'Class 0': [ciw.dists.Deterministic(1)],
                                   'Class 1': [ciw.dists.Deterministic(1)],
                                   'Class 2': [ciw.dists.Deterministic(1)]},
            number_of_servers=[10],
            batching_distributions={'Class 0': [ciw.dists.Deterministic(3)],
                                    'Class 1': [ciw.dists.Deterministic(2)],
                                    'Class 2': [ciw.dists.Deterministic(1)]}
        )
        ciw.seed(12)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(28)
        recs = Q.get_all_records()
        
        arrivals = [r.arrival_date for r in recs]
        nodes = [r.node for r in recs]
        classes = [r.customer_class for r in recs]
        self.assertEqual(arrivals, [20, 20, 20, 23, 23, 25])
        self.assertEqual(nodes, [1, 1, 1, 1, 1, 1])
        self.assertEqual(classes, [0, 0, 0, 1, 1, 2])

    def test_batching_time_dependent(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([5.0, 5.0, 2.0, 1.0, 1000.0])],
            service_distributions=[ciw.dists.Deterministic(2)],
            number_of_servers=[1],
            batching_distributions=[TimeDependentBatches()]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(30.0)
        recs = Q.get_all_records()

        self.assertEqual(len(Q.nodes[-1].all_individuals), 12)
        self.assertEqual(len(Q.nodes[1].all_individuals), 0)

        recs = Q.get_all_records()
        self.assertEqual([r.arrival_date for r in recs], [5.0, 5.0, 5.0, 5.0, 5.0, 10.0, 10.0, 10.0, 10.0, 10.0, 12.0, 13.0])
        self.assertEqual([r.exit_date for r in recs], [7.0, 9.0, 11.0, 13.0, 15.0, 17.0, 19.0, 21.0, 23.0, 25.0, 27.0, 29.0])
