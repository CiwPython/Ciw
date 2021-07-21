import unittest
import ciw

class TestProcessorSharing(unittest.TestCase):
    def test_init_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'),
            node_class=ciw.PSNode)
        N = ciw.PSNode(1, Q)
        self.assertEqual(N.ps_capacity, 9)
        self.assertEqual(N.c, float('inf'))
        self.assertEqual(N.transition_row, [[0.1, 0.2, 0.1, 0.4],
                                            [0.6, 0.0, 0.0, 0.2],
                                            [0.0, 0.0, 0.4, 0.3]])
        self.assertEqual(N.next_event_date, float('inf'))
        self.assertEqual(N.all_individuals, [])
        self.assertEqual(N.id_number, 1)
        self.assertEqual(N.interrupted_individuals, [])
        self.assertEqual(N.last_occupancy, 0)

        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_change_class.yml'),
            node_class=ciw.PSNode)
        N1 = Q.transitive_nodes[0]
        self.assertEqual(N1.class_change, [[0.5, 0.5],
                                           [0.5, 0.5]])
        N2 = Q.transitive_nodes[1]
        self.assertEqual(N2.class_change, [[1.0, 0.0],
                                           [0.0, 1.0]])
        self.assertEqual(N.interrupted_individuals, [])

        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_schedule.yml'),
            node_class=ciw.PSNode)
        N = Q.transitive_nodes[0]
        self.assertEqual(N.cyclelength, 100)
        self.assertEqual(N.ps_capacity, 1)
        self.assertEqual(N.c, float('inf'))
        self.assertEqual(N.schedule, [[0, 1], [30, 2], [60, 1], [90, 3]])
        self.assertEqual(N.next_event_date, 30)
        self.assertEqual(N.interrupted_individuals, [])
        self.assertEqual(N.last_occupancy, 0)

        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_priorities.yml'),
            node_class=ciw.PSNode)
        N = Q.transitive_nodes[0]
        self.assertEqual(N.ps_capacity, 4)
        self.assertEqual(N.c, float('inf'))
        self.assertEqual(Q.network.priority_class_mapping, {0: 0, 1: 1})
        self.assertEqual(Q.number_of_priority_classes, 2)
        self.assertEqual(N.interrupted_individuals, [])
        self.assertEqual(N.last_occupancy, 0)

    def test_update_service_end_dates_accept(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.NoArrivals()],
            service_distributions=[ciw.dists.Deterministic(1.0)],
            number_of_servers=[float('inf')]
        )
        Q = ciw.Simulation(N, node_class=ciw.PSNode)
        self.assertEqual(Q.current_time, 0.0)
        Q.current_time = 0.5
        self.assertEqual(Q.current_time, 0.5)
        ind1 = ciw.Individual(1, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind1)
        self.assertEqual(round(ind1.arrival_date, 10), 0.5)
        self.assertEqual(round(ind1.service_time, 10), 1.0)
        self.assertEqual(round(ind1.time_left, 10), 1.0)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(round(ind1.date_last_update, 10), 0.5)
        self.assertEqual(round(ind1.service_start_date, 10), 0.5)
        self.assertEqual(round(ind1.service_end_date, 10), 1.5)
        Q.current_time = 0.7
        ind2 = ciw.Individual(2, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind2)
        self.assertEqual(round(ind1.arrival_date, 10), 0.5)
        self.assertEqual(round(ind1.service_time, 10), 1.0)
        self.assertEqual(round(ind1.time_left, 10), 0.8)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(round(ind1.date_last_update, 10), 0.7)
        self.assertEqual(round(ind1.service_start_date, 10), 0.5)
        self.assertEqual(round(ind1.service_end_date, 10), 2.3)
        self.assertEqual(round(ind2.arrival_date, 10), 0.7)
        self.assertEqual(round(ind2.service_time, 10), 1.0)
        self.assertEqual(round(ind2.time_left, 10), 1.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(round(ind2.date_last_update, 10), 0.7)
        self.assertEqual(round(ind2.service_start_date, 10), 0.7)
        self.assertEqual(round(ind2.service_end_date, 10), 2.7)
        Q.current_time = 2.0
        ind3 = ciw.Individual(3, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind3)
        self.assertEqual(round(ind1.arrival_date, 10), 0.5)
        self.assertEqual(round(ind1.service_time, 10), 1.0)
        self.assertEqual(round(ind1.time_left, 10), 0.15)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(round(ind1.date_last_update, 10), 2.0)
        self.assertEqual(round(ind1.service_start_date, 10), 0.5)
        self.assertEqual(round(ind1.service_end_date, 10), 2.45)
        self.assertEqual(round(ind2.arrival_date, 10), 0.7)
        self.assertEqual(round(ind2.service_time, 10), 1.0)
        self.assertEqual(round(ind2.time_left, 10), 0.35)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(round(ind2.date_last_update, 10), 2.0)
        self.assertEqual(round(ind2.service_start_date, 10), 0.7)
        self.assertEqual(round(ind2.service_end_date, 10), 3.05)
        self.assertEqual(round(ind3.arrival_date, 10), 2.0)
        self.assertEqual(round(ind3.service_time, 10), 1.0)
        self.assertEqual(round(ind3.time_left, 10), 1.0)
        self.assertEqual(ind3.with_server, True)
        self.assertEqual(round(ind3.date_last_update, 10), 2.0)
        self.assertEqual(round(ind3.service_start_date, 10), 2.0)
        self.assertEqual(round(ind3.service_end_date, 10), 5.0)

    def test_update_service_end_dates_release(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.NoArrivals()],
            service_distributions=[ciw.dists.Sequential([1.0, 2.0, 3.0])],
            number_of_servers=[float('inf')]
        )
        Q = ciw.Simulation(N, node_class=ciw.PSNode)
        self.assertEqual(Q.current_time, 0.0)
        Q.current_time = 0.5
        self.assertEqual(Q.current_time, 0.5)
        ind1 = ciw.Individual(1, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind1)
        ind2 = ciw.Individual(2, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind2)
        ind3 = ciw.Individual(3, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind3)
        self.assertEqual(round(ind1.arrival_date, 10), 0.5)
        self.assertEqual(round(ind1.service_time, 10), 1.0)
        self.assertEqual(round(ind1.time_left, 10), 1.0)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(round(ind1.date_last_update, 10), 0.5)
        self.assertEqual(round(ind1.service_start_date, 10), 0.5)
        self.assertEqual(round(ind1.service_end_date, 10), 3.5)
        self.assertEqual(round(ind2.arrival_date, 10), 0.5)
        self.assertEqual(round(ind2.service_time, 10), 2.0)
        self.assertEqual(round(ind2.time_left, 10), 2.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(round(ind2.date_last_update, 10), 0.5)
        self.assertEqual(round(ind2.service_start_date, 10), 0.5)
        self.assertEqual(round(ind2.service_end_date, 10), 6.5)
        self.assertEqual(round(ind3.arrival_date, 10), 0.5)
        self.assertEqual(round(ind3.service_time, 10), 3.0)
        self.assertEqual(round(ind3.time_left, 10), 3.0)
        self.assertEqual(ind3.with_server, True)
        self.assertEqual(round(ind3.date_last_update, 10), 0.5)
        self.assertEqual(round(ind3.service_start_date, 10), 0.5)
        self.assertEqual(round(ind3.service_end_date, 10), 9.5)
        Q.current_time = 3.5
        Q.nodes[1].release(0, Q.nodes[-1])
        self.assertEqual(round(ind2.arrival_date, 10), 0.5)
        self.assertEqual(round(ind2.service_time, 10), 2.0)
        self.assertEqual(round(ind2.time_left, 10), 1.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(round(ind2.date_last_update, 10), 3.5)
        self.assertEqual(round(ind2.service_start_date, 10), 0.5)
        self.assertEqual(round(ind2.service_end_date, 10), 5.5)
        self.assertEqual(round(ind3.arrival_date, 10), 0.5)
        self.assertEqual(round(ind3.service_time, 10), 3.0)
        self.assertEqual(round(ind3.time_left, 10), 2.0)
        self.assertEqual(ind3.with_server, True)
        self.assertEqual(round(ind3.date_last_update, 10), 3.5)
        self.assertEqual(round(ind3.service_start_date, 10), 0.5)
        self.assertEqual(round(ind3.service_end_date, 10), 7.5)
        Q.current_time = 5.5
        Q.nodes[1].release(0, Q.nodes[-1])
        self.assertEqual(round(ind3.arrival_date, 10), 0.5)
        self.assertEqual(round(ind3.service_time, 10), 3.0)
        self.assertEqual(round(ind3.time_left, 10), 1.0)
        self.assertEqual(ind3.with_server, True)
        self.assertEqual(round(ind3.date_last_update, 10), 5.5)
        self.assertEqual(round(ind3.service_start_date, 10), 0.5)
        self.assertEqual(round(ind3.service_end_date, 10), 6.5)

    def test_ps_average_service_time(self):
        # Theory tells us that the average service time in a M/M/1-PS
        # system should be equal to 1 / (mu - lambda)
        lmbda = 3
        mu = 5
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(lmbda)],
            service_distributions=[ciw.dists.Exponential(mu)],
            number_of_servers=[float('inf')]
        )
        average_service_times = []
        for trial in range(50):
            ciw.seed(trial)
            Q = ciw.Simulation(N, node_class=ciw.PSNode)
            Q.simulate_until_max_time(400)
            recs = Q.get_all_records()
            obs_services = [r.service_time for r in recs if r.arrival_date > 30 and r.arrival_date < 370]
            average_service_times.append(sum(obs_services) / len(obs_services))
        expected = 1 / (mu - lmbda)
        observed = sum(average_service_times) / len(average_service_times)
        self.assertAlmostEqual(observed, expected, places=1)

        lmbda = 4
        mu = 5
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(lmbda)],
            service_distributions=[ciw.dists.Exponential(mu)],
            number_of_servers=[float('inf')]
        )
        average_service_times = []
        for trial in range(50):
            ciw.seed(trial)
            Q = ciw.Simulation(N, node_class=ciw.PSNode)
            Q.simulate_until_max_time(400)
            recs = Q.get_all_records()
            obs_services = [r.service_time for r in recs if r.arrival_date > 30 and r.arrival_date < 370]
            average_service_times.append(sum(obs_services) / len(obs_services))
        expected = 1 / (mu - lmbda)
        observed = sum(average_service_times) / len(average_service_times)
        self.assertAlmostEqual(observed, expected, places=1)


        lmbda = 3
        mu = 6
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(lmbda)],
            service_distributions=[ciw.dists.Exponential(mu)],
            number_of_servers=[float('inf')]
        )
        average_service_times = []
        for trial in range(50):
            ciw.seed(trial)
            Q = ciw.Simulation(N, node_class=ciw.PSNode)
            Q.simulate_until_max_time(400)
            recs = Q.get_all_records()
            obs_services = [r.service_time for r in recs if r.arrival_date > 30 and r.arrival_date < 370]
            average_service_times.append(sum(obs_services) / len(obs_services))
        expected = 1 / (mu - lmbda)
        observed = sum(average_service_times) / len(average_service_times)
        self.assertAlmostEqual(observed, expected, places=1)

    def test_limited_processor_sharing(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.NoArrivals()],
            service_distributions=[ciw.dists.Deterministic(1.0)],
            number_of_servers=[float('inf')]
        )
        Q = ciw.Simulation(N, node_class=ciw.PSNode)
        ind1 = ciw.Individual(1, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind1)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 1.0)
        ind2 = ciw.Individual(2, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind2)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 2.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(ind2.service_end_date, 2.0)
        ind3 = ciw.Individual(3, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind3)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 3.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(ind2.service_end_date, 3.0)
        self.assertEqual(ind3.with_server, True)
        self.assertEqual(ind3.service_end_date, 3.0)
        ind4 = ciw.Individual(4, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind4)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 4.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(ind2.service_end_date, 4.0)
        self.assertEqual(ind3.with_server, True)
        self.assertEqual(ind3.service_end_date, 4.0)
        self.assertEqual(ind4.with_server, True)
        self.assertEqual(ind4.service_end_date, 4.0)

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.NoArrivals()],
            service_distributions=[ciw.dists.Deterministic(1.0)],
            number_of_servers=[4]
        )
        Q = ciw.Simulation(N, node_class=ciw.PSNode)
        ind1 = ciw.Individual(1, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind1)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 1.0)
        ind2 = ciw.Individual(2, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind2)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 2.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(ind2.service_end_date, 2.0)
        ind3 = ciw.Individual(3, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind3)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 3.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(ind2.service_end_date, 3.0)
        self.assertEqual(ind3.with_server, True)
        self.assertEqual(ind3.service_end_date, 3.0)
        ind4 = ciw.Individual(4, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind4)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 4.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(ind2.service_end_date, 4.0)
        self.assertEqual(ind3.with_server, True)
        self.assertEqual(ind3.service_end_date, 4.0)
        self.assertEqual(ind4.with_server, True)
        self.assertEqual(ind4.service_end_date, 4.0)

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.NoArrivals()],
            service_distributions=[ciw.dists.Deterministic(1.0)],
            number_of_servers=[3]
        )
        Q = ciw.Simulation(N, node_class=ciw.PSNode)
        ind1 = ciw.Individual(1, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind1)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 1.0)
        ind2 = ciw.Individual(2, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind2)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 2.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(ind2.service_end_date, 2.0)
        ind3 = ciw.Individual(3, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind3)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 3.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(ind2.service_end_date, 3.0)
        self.assertEqual(ind3.with_server, True)
        self.assertEqual(ind3.service_end_date, 3.0)
        ind4 = ciw.Individual(4, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind4)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 3.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(ind2.service_end_date, 3.0)
        self.assertEqual(ind3.with_server, True)
        self.assertEqual(ind3.service_end_date, 3.0)
        self.assertEqual(ind4.with_server, False)

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.NoArrivals()],
            service_distributions=[ciw.dists.Deterministic(1.0)],
            number_of_servers=[2]
        )
        Q = ciw.Simulation(N, node_class=ciw.PSNode)
        ind1 = ciw.Individual(1, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind1)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 1.0)
        ind2 = ciw.Individual(2, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind2)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 2.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(ind2.service_end_date, 2.0)
        ind3 = ciw.Individual(3, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind3)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 2.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(ind2.service_end_date, 2.0)
        self.assertEqual(ind3.with_server, False)
        ind4 = ciw.Individual(4, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind4)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 2.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(ind2.service_end_date, 2.0)
        self.assertEqual(ind3.with_server, False)
        self.assertEqual(ind4.with_server, False)

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.NoArrivals()],
            service_distributions=[ciw.dists.Deterministic(1.0)],
            number_of_servers=[1]
        )
        Q = ciw.Simulation(N, node_class=ciw.PSNode)
        ind1 = ciw.Individual(1, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind1)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 1.0)
        ind2 = ciw.Individual(2, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind2)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 1.0)
        self.assertEqual(ind2.with_server, False)
        ind3 = ciw.Individual(3, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind3)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 1.0)
        self.assertEqual(ind2.with_server, False)
        self.assertEqual(ind3.with_server, False)
        ind4 = ciw.Individual(4, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind4)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(ind1.service_end_date, 1.0)
        self.assertEqual(ind2.with_server, False)
        self.assertEqual(ind3.with_server, False)
        self.assertEqual(ind4.with_server, False)

    def test_ps_start_waitingcustomers_service_at_release(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.NoArrivals()],
            service_distributions=[ciw.dists.Sequential([1.0, 2.0, 3.0, 4.0])],
            number_of_servers=[3]
        )
        Q = ciw.Simulation(N, node_class=ciw.PSNode)
        self.assertEqual(Q.current_time, 0.0)
        Q.current_time = 0.5
        self.assertEqual(Q.current_time, 0.5)
        ind1 = ciw.Individual(1, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind1)
        ind2 = ciw.Individual(2, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind2)
        ind3 = ciw.Individual(3, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind3)
        self.assertEqual(round(ind1.arrival_date, 10), 0.5)
        self.assertEqual(round(ind1.service_time, 10), 1.0)
        self.assertEqual(round(ind1.time_left, 10), 1.0)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(round(ind1.date_last_update, 10), 0.5)
        self.assertEqual(round(ind1.service_start_date, 10), 0.5)
        self.assertEqual(round(ind1.service_end_date, 10), 3.5)
        self.assertEqual(round(ind2.arrival_date, 10), 0.5)
        self.assertEqual(round(ind2.service_time, 10), 2.0)
        self.assertEqual(round(ind2.time_left, 10), 2.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(round(ind2.date_last_update, 10), 0.5)
        self.assertEqual(round(ind2.service_start_date, 10), 0.5)
        self.assertEqual(round(ind2.service_end_date, 10), 6.5)
        self.assertEqual(round(ind3.arrival_date, 10), 0.5)
        self.assertEqual(round(ind3.service_time, 10), 3.0)
        self.assertEqual(round(ind3.time_left, 10), 3.0)
        self.assertEqual(ind3.with_server, True)
        self.assertEqual(round(ind3.date_last_update, 10), 0.5)
        self.assertEqual(round(ind3.service_start_date, 10), 0.5)
        self.assertEqual(round(ind3.service_end_date, 10), 9.5)
        Q.current_time = 1.5
        ind4 = ciw.Individual(4, customer_class=0, priority_class=0, simulation=Q)
        Q.nodes[1].accept(ind4)
        self.assertEqual(round(ind1.arrival_date, 10), 0.5)
        self.assertEqual(round(ind1.service_time, 10), 1.0)
        self.assertEqual(round(ind1.time_left, 10), 1.0)
        self.assertEqual(ind1.with_server, True)
        self.assertEqual(round(ind1.date_last_update, 10), 0.5)
        self.assertEqual(round(ind1.service_start_date, 10), 0.5)
        self.assertEqual(round(ind1.service_end_date, 10), 3.5)
        self.assertEqual(round(ind2.arrival_date, 10), 0.5)
        self.assertEqual(round(ind2.service_time, 10), 2.0)
        self.assertEqual(round(ind2.time_left, 10), 2.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(round(ind2.date_last_update, 10), 0.5)
        self.assertEqual(round(ind2.service_start_date, 10), 0.5)
        self.assertEqual(round(ind2.service_end_date, 10), 6.5)
        self.assertEqual(round(ind3.arrival_date, 10), 0.5)
        self.assertEqual(round(ind3.service_time, 10), 3.0)
        self.assertEqual(round(ind3.time_left, 10), 3.0)
        self.assertEqual(ind3.with_server, True)
        self.assertEqual(round(ind3.date_last_update, 10), 0.5)
        self.assertEqual(round(ind3.service_start_date, 10), 0.5)
        self.assertEqual(round(ind3.service_end_date, 10), 9.5)
        self.assertEqual(ind4.with_server, False)
        Q.current_time = 3.5
        Q.nodes[1].release(0, Q.nodes[-1])
        self.assertEqual(round(ind2.arrival_date, 10), 0.5)
        self.assertEqual(round(ind2.service_time, 10), 2.0)
        self.assertEqual(round(ind2.time_left, 10), 1.0)
        self.assertEqual(ind2.with_server, True)
        self.assertEqual(round(ind2.date_last_update, 10), 3.5)
        self.assertEqual(round(ind2.service_start_date, 10), 0.5)
        self.assertEqual(round(ind2.service_end_date, 10), 6.5)
        self.assertEqual(round(ind3.arrival_date, 10), 0.5)
        self.assertEqual(round(ind3.service_time, 10), 3.0)
        self.assertEqual(round(ind3.time_left, 10), 2.0)
        self.assertEqual(ind3.with_server, True)
        self.assertEqual(round(ind3.date_last_update, 10), 3.5)
        self.assertEqual(round(ind3.service_start_date, 10), 0.5)
        self.assertEqual(round(ind3.service_end_date, 10), 9.5)
        self.assertEqual(round(ind4.arrival_date, 10), 1.5)
        self.assertEqual(round(ind4.service_time, 10), 4.0)
        self.assertEqual(round(ind4.time_left, 10), 4.0)
        self.assertEqual(ind4.with_server, True)
        self.assertEqual(round(ind4.date_last_update, 10), 3.5)
        self.assertEqual(round(ind4.service_start_date, 10), 3.5)
        self.assertEqual(round(ind4.service_end_date, 10), 15.5)
        Q.current_time = 6.5
        Q.nodes[1].release(0, Q.nodes[-1])
        self.assertEqual(round(ind3.arrival_date, 10), 0.5)
        self.assertEqual(round(ind3.service_time, 10), 3.0)
        self.assertEqual(round(ind3.time_left, 10), 1.0)
        self.assertEqual(ind3.with_server, True)
        self.assertEqual(round(ind3.date_last_update, 10), 6.5)
        self.assertEqual(round(ind3.service_start_date, 10), 0.5)
        self.assertEqual(round(ind3.service_end_date, 10), 8.5)
        self.assertEqual(round(ind4.arrival_date, 10), 1.5)
        self.assertEqual(round(ind4.service_time, 10), 4.0)
        self.assertEqual(round(ind4.time_left, 10), 3.0)
        self.assertEqual(ind4.with_server, True)
        self.assertEqual(round(ind4.date_last_update, 10), 6.5)
        self.assertEqual(round(ind4.service_start_date, 10), 3.5)
        self.assertEqual(round(ind4.service_end_date, 10), 12.5)

    def test_capacitated_ps(self):
        # Compare to theory
        # Expected:
        # {0: 0.4321329639889196,
        #  1: 0.3601108033240997,
        #  2: 0.1500461680517082,
        #  3: 0.041679491125474505,
        #  4: 0.011577636423742918,
        #  5: 0.003216010117706367,
        #  6: 0.0008933361438073241,
        #  7: 0.0002481489288353678,
        #  8: 6.89302580098244e-05}
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(10)],
            service_distributions=[ciw.dists.Exponential(12)],
            number_of_servers=[float('inf')],
            ps_thresholds=[3]
        )
        ciw.seed(0)
        Q = ciw.Simulation(N, node_class=ciw.PSNode, tracker=ciw.trackers.SystemPopulation())
        Q.simulate_until_max_time(1000)
        probs = Q.statetracker.state_probabilities()
        self.assertEqual(round(probs[0], 7), 0.4418991)
        self.assertEqual(round(probs[1], 7), 0.3615230)
        self.assertEqual(round(probs[2], 7), 0.1458424)
        self.assertEqual(round(probs[3], 7), 0.0390748)
        self.assertEqual(round(probs[4], 7), 0.0089170)
        self.assertEqual(round(probs[5], 7), 0.0018729)
        self.assertEqual(round(probs[6], 7), 0.0006893)
        self.assertEqual(round(probs[7], 7), 0.0000758)
        self.assertEqual(round(probs[8], 7), 0.0001057)
