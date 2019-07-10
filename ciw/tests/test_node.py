import unittest
import ciw
from hypothesis import given, settings
from hypothesis.strategies import floats, integers, random_module

class TestNode(unittest.TestCase):
    def test_init_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        N = ciw.Node(1, Q)
        self.assertEqual(N.c, 9)
        self.assertEqual(N.transition_row, [[0.1, 0.2, 0.1, 0.4],
                                            [0.6, 0.0, 0.0, 0.2],
                                            [0.0, 0.0, 0.4, 0.3]])
        self.assertEqual(N.next_event_date, float('inf'))
        self.assertEqual(N.all_individuals, [])
        self.assertEqual(N.id_number, 1)
        self.assertEqual(N.interrupted_individuals, [])

        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_change_class.yml'))
        N1 = Q.transitive_nodes[0]
        self.assertEqual(N1.class_change, [[0.5, 0.5],
                                           [0.5, 0.5]])
        N2 = Q.transitive_nodes[1]
        self.assertEqual(N2.class_change, [[1.0, 0.0],
                                           [0.0, 1.0]])
        self.assertEqual(N.interrupted_individuals, [])

        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_schedule.yml'))
        N = Q.transitive_nodes[0]
        self.assertEqual(N.cyclelength, 100)
        self.assertEqual(N.c, 1)
        self.assertEqual(N.schedule, [[0, 1], [30, 2], [60, 1], [90, 3]])
        self.assertEqual(N.next_event_date, 30)
        self.assertEqual(N.interrupted_individuals, [])

        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_priorities.yml'))
        N = Q.transitive_nodes[0]
        self.assertEqual(N.c, 4)
        self.assertEqual(Q.network.priority_class_mapping, {0: 0, 1: 1})
        self.assertEqual(Q.number_of_priority_classes, 2)
        self.assertEqual(N.interrupted_individuals, [])

    def test_repr_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        N1 = ciw.Node(1, Q)
        N2 = ciw.Node(2, Q)
        self.assertEqual(str(N1), 'Node 1')
        self.assertEqual(str(N2), 'Node 2')

    def test_finish_service_method(self):
        ciw.seed(4)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        N = Q.transitive_nodes[0]
        inds = [ciw.Individual(i + 1) for i in range(3)]
        for current_time in [0.01, 0.02, 0.03]:
            Q.current_time = current_time
            N.accept(inds[int(current_time*100 - 1)])
        self.assertEqual([str(obs) for obs in N.all_individuals],
            ['Individual 1', 'Individual 2', 'Individual 3'])
        self.assertEqual(
            [[str(obs) for obs in pr_cls] for pr_cls in N.individuals],
            [['Individual 1', 'Individual 2', 'Individual 3']])
        Q.current_time = 0.03
        N.update_next_event_date()
        self.assertEqual(round(N.next_event_date, 5), 0.03604)
        N.finish_service()
        self.assertEqual([str(obs) for obs in N.all_individuals],
            ['Individual 1', 'Individual 3'])
        self.assertEqual(
            [[str(obs) for obs in pr_cls] for pr_cls in N.individuals],
            [['Individual 1', 'Individual 3']])

    def test_change_customer_class_method(self):
        ciw.seed(14)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_change_class.yml'))
        N1 = Q.transitive_nodes[0]
        ind = ciw.Individual(254, 0)
        self.assertEqual(ind.customer_class, 0)
        self.assertEqual(ind.previous_class, 0)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 0)
        self.assertEqual(ind.previous_class, 0)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 0)
        self.assertEqual(ind.previous_class, 0)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 1)
        self.assertEqual(ind.previous_class, 0)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 1)
        self.assertEqual(ind.previous_class, 1)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 0)
        self.assertEqual(ind.previous_class, 1)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 1)
        self.assertEqual(ind.previous_class, 0)

        # Test for case of having priorities
        ciw.seed(14)
        parameters_dictionary = {
            'arrival_distributions': {'Class 0': [ciw.dists.Exponential(0.05), ciw.dists.Exponential(0.04)],
                                      'Class 1': [ciw.dists.Exponential(0.04), ciw.dists.Exponential(0.06)]},
            'service_distributions': {'Class 0': [ciw.dists.Deterministic(5), ciw.dists.Deterministic(5)],
                                      'Class 1': [ciw.dists.Deterministic(10), ciw.dists.Deterministic(10)]},
            'routing': {'Class 0': [[0.8, 0.1], [0.0, 0.0]],
                        'Class 1': [[0.8, 0.1], [0.2, 0.0]]},
            'number_of_servers': [4, 3],
            'class_change_matrices': {'Node 1': [[.5, .5], [.25, .75]],
                                      'Node 2': [[1, 0], [0, 1]]},
            'priority_classes': {'Class 0': 0, 'Class 1': 1}
        }
        Q = ciw.Simulation(ciw.create_network_from_dictionary(parameters_dictionary))
        N1 = Q.transitive_nodes[0]
        ind = ciw.Individual(254, 0)
        self.assertEqual(ind.customer_class, 0)
        self.assertEqual(ind.priority_class, 0)
        self.assertEqual(ind.previous_class, 0)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 0)
        self.assertEqual(ind.priority_class, 0)
        self.assertEqual(ind.previous_class, 0)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 0)
        self.assertEqual(ind.priority_class, 0)
        self.assertEqual(ind.previous_class, 0)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 1)
        self.assertEqual(ind.priority_class, 1)
        self.assertEqual(ind.previous_class, 0)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 1)
        self.assertEqual(ind.priority_class, 1)
        self.assertEqual(ind.previous_class, 1)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 1)
        self.assertEqual(ind.priority_class, 1)
        self.assertEqual(ind.previous_class, 1)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 1)
        self.assertEqual(ind.priority_class, 1)
        self.assertEqual(ind.previous_class, 1)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 1)
        self.assertEqual(ind.priority_class, 1)
        self.assertEqual(ind.previous_class, 1)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 1)
        self.assertEqual(ind.priority_class, 1)
        self.assertEqual(ind.previous_class, 1)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 0)
        self.assertEqual(ind.priority_class, 0)
        self.assertEqual(ind.previous_class, 1)
        N1.change_customer_class(ind)
        self.assertEqual(ind.customer_class, 0)
        self.assertEqual(ind.priority_class, 0)
        self.assertEqual(ind.previous_class, 0)

    def test_block_individual_method(self):
        ciw.seed(4)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_deadlock.yml'),
            deadlock_detector=ciw.deadlock.StateDigraph())
        inds = [ciw.Individual(i + 1) for i in range(7)]
        N1 = Q.transitive_nodes[0]
        N1.individuals = [inds[:6]]
        N2 = Q.transitive_nodes[1]
        Q.current_time = 2
        N2.accept(inds[6])
        self.assertEqual(inds[6].is_blocked, False)
        self.assertEqual(N1.blocked_queue, [])
        self.assertEqual(set(Q.deadlock_detector.statedigraph.edges()), set([]))
        N2.block_individual(inds[6], N1)
        self.assertEqual(inds[6].is_blocked, True)
        [(2, 7)]
        self.assertEqual(set(Q.deadlock_detector.statedigraph.edges()),
            set([('Server 1 at Node 2', 'Server 2 at Node 1'),
                 ('Server 1 at Node 2', 'Server 5 at Node 1'),
                 ('Server 1 at Node 2', 'Server 3 at Node 1'),
                 ('Server 1 at Node 2', 'Server 1 at Node 1'),
                 ('Server 1 at Node 2', 'Server 4 at Node 1')]))

    def test_release_method(self):
        ciw.seed(4)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        N = Q.transitive_nodes[0]
        inds = [ciw.Individual(i+1) for i in range(3)]
        for current_time in [0.01, 0.02, 0.03]:
            Q.current_time = current_time
            N.accept(inds[int(current_time*100 - 1)])
        self.assertEqual([str(obs) for obs in N.all_individuals],
            ['Individual 1', 'Individual 2', 'Individual 3'])
        self.assertEqual(
            [[str(obs) for obs in pr_cls] for pr_cls in N.individuals],
            [['Individual 1', 'Individual 2', 'Individual 3']])
        Q.current_time = 0.03
        N.update_next_event_date()
        self.assertEqual(round(N.next_event_date, 5), 0.03604)

        N.servers[1].next_end_service_date = float('inf')
        N.release(1, Q.transitive_nodes[1])
        self.assertEqual([str(obs) for obs in N.all_individuals],
            ['Individual 1', 'Individual 3'])
        self.assertEqual(
            [[str(obs) for obs in pr_cls] for pr_cls in N.individuals],
            [['Individual 1', 'Individual 3']])
        N.update_next_event_date()
        self.assertEqual(round(N.next_event_date, 5), 0.03708)

        N.servers[0].next_end_service_date = float('inf')
        N.release(0, Q.transitive_nodes[1])
        self.assertEqual([str(obs) for obs in N.all_individuals],
            ['Individual 3'])
        self.assertEqual(
            [[str(obs) for obs in pr_cls] for pr_cls in N.individuals],
            [['Individual 3']])
        N.update_next_event_date()
        self.assertEqual(round(N.next_event_date, 5), 0.06447)

    def test_begin_service_if_possible_release_method(self):
        ciw.seed(50)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_deadlock.yml'),
            deadlock_detector=ciw.deadlock.StateDigraph())
        inds = [[ciw.Individual(i) for i in range(30)]]
        Q.transitive_nodes[0].individuals = inds
        ind = Q.transitive_nodes[0].individuals[0][0]
        ind.arrival_date = 100.0
        self.assertEqual(set(Q.deadlock_detector.statedigraph.nodes()),
            set(['Server 5 at Node 2',
                 'Server 5 at Node 1',
                 'Server 3 at Node 2',
                 'Server 1 at Node 2',
                 'Server 1 at Node 1',
                 'Server 2 at Node 1',
                 'Server 2 at Node 2',
                 'Server 3 at Node 1',
                 'Server 4 at Node 1',
                 'Server 4 at Node 2']))
        self.assertEqual(ind.arrival_date, 100.0)
        self.assertEqual(ind.service_time, False)
        self.assertEqual(ind.service_start_date, False)
        self.assertEqual(ind.service_end_date, False)
        Q.current_time = 200.0
        Q.transitive_nodes[0].begin_service_if_possible_release()
        self.assertEqual(ind.arrival_date, 100.0)
        self.assertEqual(round(ind.service_time, 5), 0.03382)
        self.assertEqual(ind.service_start_date, 200.0)
        self.assertEqual(round(ind.service_end_date, 5), 200.03382)

    def test_release_blocked_individual_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_deadlock.yml'),
            deadlock_detector=ciw.deadlock.StateDigraph())
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]
        N1.individuals = [[ciw.Individual(i) for i in range(N1.c + 3)]]
        N2.individuals = [[ciw.Individual(i + 100) for i in range(N2.c + 4)]]
        for ind in N1.all_individuals[:2]:
            N1.attach_server(N1.find_free_server(), ind)
        for ind in N2.all_individuals[:1]:
            N2.attach_server(N2.find_free_server(), ind)

        self.assertEqual([str(obs) for obs in N1.all_individuals],
            ['Individual 0',
             'Individual 1',
             'Individual 2',
             'Individual 3',
             'Individual 4',
             'Individual 5',
             'Individual 6',
             'Individual 7'])
        self.assertEqual([str(obs) for obs in N2.all_individuals],
            ['Individual 100',
             'Individual 101',
             'Individual 102',
             'Individual 103',
             'Individual 104',
             'Individual 105',
             'Individual 106',
             'Individual 107',
             'Individual 108'])
        Q.current_time = 100
        N1.release_blocked_individual()
        self.assertEqual([str(obs) for obs in N1.all_individuals],
            ['Individual 0',
             'Individual 1',
             'Individual 2',
             'Individual 3',
             'Individual 4',
             'Individual 5',
             'Individual 6',
             'Individual 7'])
        self.assertEqual([str(obs) for obs in N2.all_individuals],
            ['Individual 100',
             'Individual 101',
             'Individual 102',
             'Individual 103',
             'Individual 104',
             'Individual 105',
             'Individual 106',
             'Individual 107',
             'Individual 108'])

        N1.blocked_queue = [(1, 1), (2, 100)]
        N1.len_blocked_queue = 2
        rel_ind = N1.individuals[0].pop(0)
        N1.detatch_server(rel_ind.server, rel_ind)

        Q.current_time = 110
        N1.release_blocked_individual()
        self.assertEqual([str(obs) for obs in N1.all_individuals],
            ['Individual 2',
             'Individual 3',
             'Individual 4',
             'Individual 5',
             'Individual 6',
             'Individual 7',
             'Individual 1',
             'Individual 100'])
        self.assertEqual([str(obs) for obs in N2.all_individuals],
            ['Individual 101',
             'Individual 102',
             'Individual 103',
             'Individual 104',
             'Individual 105',
             'Individual 106',
             'Individual 107',
             'Individual 108'])

    def test_accept_method(self):
        ciw.seed(6)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        N = Q.transitive_nodes[0]
        N.next_event_date = 0.0
        self.assertEqual(N.all_individuals, [])
        ind1 = ciw.Individual(1)
        ind2 = ciw.Individual(2)
        ind3 = ciw.Individual(3)
        ind4 = ciw.Individual(4)
        ind5 = ciw.Individual(5)
        ind6 = ciw.Individual(6)
        ind7 = ciw.Individual(7)
        ind8 = ciw.Individual(8)
        ind9 = ciw.Individual(9)
        ind10 = ciw.Individual(10)

        Q.current_time = 0.01
        N.accept(ind1)
        self.assertEqual([str(obs) for obs in N.all_individuals],
            ['Individual 1'])
        self.assertEqual(ind1.arrival_date, 0.01)
        self.assertEqual(ind1.service_start_date, 0.01)
        self.assertEqual(round(ind1.service_time, 5), 0.18695)
        self.assertEqual(round(ind1.service_end_date, 5), 0.19695)

        Q.current_time = 0.02
        N.accept(ind2)
        Q.current_time = 0.03
        N.accept(ind3)
        Q.current_time = 0.04
        N.accept(ind4)
        self.assertEqual([str(obs) for obs in N.all_individuals],
            ['Individual 1',
             'Individual 2',
             'Individual 3',
             'Individual 4'])
        self.assertEqual(round(ind4.arrival_date, 5), 0.04)
        self.assertEqual(round(ind4.service_start_date, 5), 0.04)
        self.assertEqual(round(ind4.service_time, 5), 0.1637)
        self.assertEqual(round(ind4.service_end_date, 5), 0.2037)

        Q.current_time = 0.05
        N.accept(ind5)
        Q.current_time = 0.06
        N.accept(ind6)
        Q.current_time = 0.07
        N.accept(ind7)
        Q.current_time = 0.08
        N.accept(ind8)
        Q.current_time = 0.09
        N.accept(ind9)
        Q.current_time = 0.1
        N.accept(ind10)
        self.assertEqual([str(obs) for obs in N.all_individuals],
            ['Individual 1',
             'Individual 2',
             'Individual 3',
             'Individual 4',
             'Individual 5',
             'Individual 6',
             'Individual 7',
             'Individual 8',
             'Individual 9',
             'Individual 10'])
        self.assertEqual(round(ind10.arrival_date, 5), 0.1)
        self.assertEqual(ind10.service_start_date, False)
        self.assertEqual(ind10.service_time, False)

    def test_begin_service_if_possible_accept_method(self):
        ciw.seed(50)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_deadlock.yml'),
            deadlock_detector=ciw.deadlock.StateDigraph())
        ind = ciw.Individual(1)
        self.assertEqual(set(Q.deadlock_detector.statedigraph.nodes()),
            set(['Server 5 at Node 2',
                 'Server 5 at Node 1',
                 'Server 3 at Node 2',
                 'Server 1 at Node 2',
                 'Server 1 at Node 1',
                 'Server 2 at Node 1',
                 'Server 2 at Node 2',
                 'Server 3 at Node 1',
                 'Server 4 at Node 1',
                 'Server 4 at Node 2']))
        self.assertEqual(ind.arrival_date, False)
        self.assertEqual(ind.service_time, False)
        self.assertEqual(ind.service_start_date, False)
        self.assertEqual(ind.service_end_date, False)
        Q.current_time = 300
        Q.transitive_nodes[0].begin_service_if_possible_accept(ind)
        self.assertEqual(ind.arrival_date, 300)
        self.assertEqual(round(ind.service_time, 5), 0.03382)
        self.assertEqual(ind.service_start_date, 300)
        self.assertEqual(round(ind.service_end_date, 5), 300.03382)

    def test_update_next_event_date_method(self):
        Net = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(10.0)],
            service_distributions=[ciw.dists.Sequential([0.5, 0.2])],
            number_of_servers=[5]
        )
        Q = ciw.Simulation(Net)
        N = Q.transitive_nodes[0]
        self.assertEqual(N.next_event_date, float('inf'))
        self.assertEqual(N.all_individuals, [])
        Q.current_time = 0.0
        N.update_next_event_date()
        self.assertEqual(N.next_event_date, float('inf'))

        ind1 = ciw.Individual(1)
        ind1.arrival_date = 0.3
        N.next_event_date = 0.3
        Q.current_time = 0.3
        N.accept(ind1)
        N.update_next_event_date()
        self.assertEqual(N.next_event_date, 0.8)

        ind2 = ciw.Individual(2)
        ind2.arrival_date = 0.4
        Q.current_time = 0.4
        N.accept(ind2)
        Q.current_time = N.next_event_date + 0.000001
        N.update_next_event_date()
        self.assertEqual(round(N.next_event_date, 4), 0.6)

        N.finish_service()
        N.update_next_event_date()
        self.assertEqual(N.next_event_date, 0.8)

        N.finish_service()
        N.update_next_event_date()
        self.assertEqual(N.next_event_date, float('inf'))

    def test_next_node_method(self):
        ciw.seed(6)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        node = Q.transitive_nodes[0]
        ind = ciw.Individual(22)
        self.assertEqual(str(node.next_node(ind)), 'Node 4')
        self.assertEqual(str(node.next_node(ind)), 'Node 4')
        self.assertEqual(str(node.next_node(ind)), 'Node 4')
        self.assertEqual(str(node.next_node(ind)), 'Node 4')
        self.assertEqual(str(node.next_node(ind)), 'Node 2')
        self.assertEqual(str(node.next_node(ind)), 'Node 4')
        self.assertEqual(str(node.next_node(ind)), 'Exit Node')
        self.assertEqual(str(node.next_node(ind)), 'Node 2')
        self.assertEqual(str(node.next_node(ind)), 'Exit Node')
        self.assertEqual(str(node.next_node(ind)), 'Node 4')

        ciw.seed(54)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        node = Q.transitive_nodes[2]
        self.assertEqual(str(node.next_node(ind)), 'Node 2')
        self.assertEqual(str(node.next_node(ind)), 'Node 4')
        self.assertEqual(str(node.next_node(ind)), 'Node 2')
        self.assertEqual(str(node.next_node(ind)), 'Node 2')
        self.assertEqual(str(node.next_node(ind)), 'Node 2')
        self.assertEqual(str(node.next_node(ind)), 'Node 2')
        self.assertEqual(str(node.next_node(ind)), 'Node 4')
        self.assertEqual(str(node.next_node(ind)), 'Node 2')
        self.assertEqual(str(node.next_node(ind)), 'Node 2')
        self.assertEqual(str(node.next_node(ind)), 'Node 4')
        self.assertEqual(str(node.next_node(ind)), 'Node 2')
        self.assertEqual(str(node.next_node(ind)), 'Node 2')
        self.assertEqual(str(node.next_node(ind)), 'Node 2')
        self.assertEqual(str(node.next_node(ind)), 'Node 3')
        self.assertEqual(str(node.next_node(ind)), 'Node 2')
        self.assertEqual(str(node.next_node(ind)), 'Node 2')

    def test_write_individual_record_method(self):
        ciw.seed(7)
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        N = Q.transitive_nodes[0]
        ind = ciw.Individual(6)
        Q.current_time = 3
        N.accept(ind)
        ind.service_start_date = 3.5
        ind.service_end_date = 5.5
        ind.exit_date = 9
        N.write_individual_record(ind)
        self.assertEqual(ind.data_records[0].arrival_date, 3)
        self.assertEqual(ind.data_records[0].waiting_time, 0.5)
        self.assertEqual(ind.data_records[0].service_start_date, 3.5)
        self.assertEqual(ind.data_records[0].service_time, 2)
        self.assertEqual(ind.data_records[0].service_end_date, 5.5)
        self.assertEqual(ind.data_records[0].time_blocked, 3.5)
        self.assertEqual(ind.data_records[0].exit_date, 9)
        self.assertEqual(ind.data_records[0].customer_class, 0)

    def test_date_from_schedule_generator(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))

        sg = Q.nodes[1].date_from_schedule_generator([30, 60, 90, 100])
        self.assertEqual(next(sg), 30)
        self.assertEqual(next(sg), 60)
        self.assertEqual(next(sg), 90)
        self.assertEqual(next(sg), 100)
        self.assertEqual(next(sg), 130)
        self.assertEqual(next(sg), 160)

    def test_all_individuals_property(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_priorities.yml'))
        N1 = Q.transitive_nodes[0]
        self.assertEqual(N1.individuals, [[], []])
        self.assertEqual(N1.all_individuals, [])

        N1.individuals = [[3, 6, 1], [1, 9]]
        self.assertEqual(N1.all_individuals, [3, 6, 1, 1, 9])

        N1.individuals = [[3, 'help', 1], [], [1, 9]]
        self.assertEqual(N1.all_individuals, [3, 'help', 1, 1, 9])

    def test_if_putting_individuals_in_correct_priority_queue(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_priorities.yml'))
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]

        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N1.individuals], [[], []])
        self.assertEqual(
            [str(obs) for obs in N1.all_individuals], [])
        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N2.individuals], [[], []])
        self.assertEqual(
            [str(obs) for obs in N2.all_individuals], [])

        Q.nodes[0].next_node = 1
        Q.nodes[0].next_class = 0
        Q.nodes[0].have_event()

        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N1.individuals],
            [['Individual 1'], []])
        self.assertEqual(
            [str(obs) for obs in N1.all_individuals],
            ['Individual 1'])
        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N2.individuals], [[], []])
        self.assertEqual(
            [str(obs) for obs in N2.all_individuals], [])

        Q.nodes[0].next_node = 1
        Q.nodes[0].next_class = 1
        Q.nodes[0].have_event()

        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N1.individuals],
            [['Individual 1'], ['Individual 2']])
        self.assertEqual(
            [str(obs) for obs in N1.all_individuals],
            ['Individual 1', 'Individual 2'])
        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N2.individuals], [[], []])
        self.assertEqual(
            [str(obs) for obs in N2.all_individuals], [])

        Q.nodes[0].next_node = 2
        Q.nodes[0].next_class = 0
        Q.nodes[0].have_event()

        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N1.individuals],
            [['Individual 1'], ['Individual 2']])
        self.assertEqual(
            [str(obs) for obs in N1.all_individuals],
            ['Individual 1', 'Individual 2'])
        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N2.individuals],
            [['Individual 3'], []])
        self.assertEqual(
            [str(obs) for obs in N2.all_individuals],
            ['Individual 3'])

        Q.nodes[0].next_node = 2
        Q.nodes[0].next_class = 1
        Q.nodes[0].have_event()

        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N1.individuals],
            [['Individual 1'], ['Individual 2']])
        self.assertEqual(
            [str(obs) for obs in N1.all_individuals],
            ['Individual 1', 'Individual 2'])
        self.assertEqual(
            [[str(obs) for obs in lst] for lst in N2.individuals],
            [['Individual 3'], ['Individual 4']])
        self.assertEqual(
            [str(obs) for obs in N2.all_individuals],
            ['Individual 3', 'Individual 4'])

    def test_server_utilisation(self):
        # Single server
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([2.0, 3.0, 100.0])],
            service_distributions=[ciw.dists.Sequential([1.0, 6.0, 100.0])],
            number_of_servers=[1],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(14.0)
        self.assertEqual(Q.transitive_nodes[0].server_utilisation, 0.5)

        # Multi server
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([2.0, 3.0, 100.0])],
            service_distributions=[ciw.dists.Sequential([10.0, 6.0, 100.0])],
            number_of_servers=[3],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20.0)
        self.assertEqual(Q.transitive_nodes[0].server_utilisation, 4.0/15.0)

    def test_server_utilisation_with_schedules(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([2.0, 4.0, 4.0, 0.0, 7.0, 1000.0])],
            service_distributions=[ciw.dists.Sequential([4.0, 2.0, 6.0, 6.0, 3.0])],
            number_of_servers=[[[1, 9], [2, 23]]]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(23)
        recs = Q.get_all_records()
        self.assertEqual(Q.transitive_nodes[0].server_utilisation, 21.0/37.0)

    def test_server_utilisation_with_wrapup(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(7.14)],
            service_distributions=[ciw.dists.Exponential(0.04)],
            number_of_servers=[70]
        )
        ciw.seed(1)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(168)
        for srvr in Q.transitive_nodes[0].servers:
            self.assertGreaterEqual(srvr.total_time, srvr.busy_time)

    @given(lmbda=floats(min_value=0.01, max_value=10),
           mu=floats(min_value=0.01, max_value=10),
           c=integers(min_value=1, max_value=10),
           rm=random_module())
    def test_utilisation_always_1_or_less(self, lmbda, mu, c, rm):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(lmbda)],
            service_distributions=[ciw.dists.Exponential(mu)],
            number_of_servers=[c]
        )
        ciw.seed(1)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(200)
        for srvr in Q.transitive_nodes[0].servers:
            self.assertGreaterEqual(srvr.total_time, srvr.busy_time)
        self.assertLessEqual(Q.transitive_nodes[0].server_utilisation, 1.0)
        self.assertGreaterEqual(Q.transitive_nodes[0].server_utilisation, 0.0)

    def test_num_inds_equal_len_all_inds(self):
        # Create a Simulation class that inherits from ciw.Simulation so that
        # an assertion than number_of_individuals == len(all_individuals)
        # every time self.event_and_return_nextnode is called.
        class AssertSim(ciw.Simulation):
            def event_and_return_nextnode(simself, next_active_node):
                """
                Carries out the event of current next_active_node, and return the next
                next_active_node
                """
                next_active_node.have_event()
                for node in simself.transitive_nodes:
                    node.update_next_event_date()
                    self.assertEqual(
                        node.number_of_individuals, len(node.all_individuals))
                return simself.find_next_active_node()

        # Now carry out the tests by running a simulation with this new
        # inherited Node class.
        N = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = AssertSim(N)
        Q.simulate_until_max_time(100)
