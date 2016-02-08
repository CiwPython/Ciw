import unittest
import ciw
from random import seed

class TestNode(unittest.TestCase):

    def test_init_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        N = ciw.Node(1, Q)
        self.assertEqual(N.mu, [['Exponential', 7.0], ['Exponential', 7.0], ['Deterministic', 0.3]])
        self.assertEqual(N.c, 9)
        self.assertEqual(N.transition_row, [[0.1, 0.2, 0.1, 0.4], [0.6, 0.0, 0.0, 0.2], [0.0, 0.0, 0.4, 0.3]])
        self.assertEqual(N.next_event_date, 'Inf')
        self.assertEqual(N.individuals, [])
        self.assertEqual(N.id_number, 1)
        self.assertEqual([[round(obs, 1) for obs in row] for row in N.cum_transition_row], [[0.1, 0.3, 0.4, 0.8], [0.6, 0.6, 0.6, 0.8], [0.0, 0.0, 0.4, 0.7]])

        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_dynamic_classes/parameters.yml'))
        N1 = Q.transitive_nodes[0]
        self.assertEqual(N1.class_change_for_node, [[0.7, 0.3], [0.2, 0.8]])
        N2 = Q.transitive_nodes[1]
        self.assertEqual(N2.class_change_for_node, [[1.0, 0.0], [0.0, 1.0]])
       
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_server_schedule/parameters.yml'))
        N = Q.transitive_nodes[0]
        self.assertEqual(N.scheduled_servers, True)
        self.assertEqual(N.cyclelength, 100)
        self.assertEqual(N.c, 1)
        self.assertEqual(N.masterschedule, [30, 60, 90, 100, 130, 160, 190, 200, 230, 260, 290, 300, 330, 360, 390])
        self.assertEqual(N.next_event_date, 30)

    def test_find_cdf_class_changes_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_dynamic_classes/parameters.yml'))
        N1 = Q.transitive_nodes[0]
        self.assertEqual(N1.find_cdf_class_changes(), [[0.7, 1.0], [0.2, 1.0]])

    def test_find_cum_transition_row_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        N = ciw.Node(1, Q)
        self.assertEqual([[round(obs, 1) for obs in row] for row in N.find_cum_transition_row()], [[0.1, 0.3, 0.4, 0.8], [0.6, 0.6, 0.6, 0.8], [0.0, 0.0, 0.4, 0.7]])

    def test_repr_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        N1 = ciw.Node(1, Q)
        N2 = ciw.Node(2, Q)
        self.assertEqual(str(N1), 'Node 1')
        self.assertEqual(str(N2), 'Node 2')

    def test_change_shift_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_server_schedule/parameters.yml'))
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

    def test_take_servers_off_duty_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_server_schedule/parameters.yml'))
        N = Q.transitive_nodes[0]
        N.add_new_server(3, 1)
        self.assertEqual([str(obs) for obs in N.servers], ['Server 1 at Node 1', 'Server 2 at Node 1', 'Server 3 at Node 1', 'Server 4 at Node 1'])
        N.servers[1].busy = True
        N.servers[2].busy = True
        self.assertEqual([obs.busy for obs in N.servers], [False, True, True, False])
        self.assertEqual([obs.offduty for obs in N.servers], [False, False, False, False])
        N.take_servers_off_duty()
        self.assertEqual([str(obs) for obs in N.servers], ['Server 2 at Node 1', 'Server 3 at Node 1'])
        self.assertEqual([obs.busy for obs in N.servers], [True, True])
        self.assertEqual([obs.offduty for obs in N.servers], [True, True])

    def test_check_if_shiftchange_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_server_schedule/parameters.yml'))
        N = Q.transitive_nodes[0]
        N.next_event_date = 12.0
        self.assertEqual(N.check_if_shiftchange(), False)
        N.next_event_date = 30.0
        self.assertEqual(N.check_if_shiftchange(), True)

        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        N = Q.transitive_nodes[0]
        N.next_event_date = 12.0
        self.assertEqual(N.check_if_shiftchange(), False)
        N.next_event_date = 30.0
        self.assertEqual(N.check_if_shiftchange(), False)

    def test_finish_service_method(self):
        seed(4)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        N = Q.transitive_nodes[0]
        inds = [ciw.Individual(i+1) for i in range(3)]
        for current_time in [0.01, 0.02, 0.03]:
            N.accept(inds[int(current_time*100 - 1)], current_time)
        self.assertEqual([str(obs) for obs in N.individuals], ['Individual 1', 'Individual 2', 'Individual 3'])
        N.update_next_event_date(0.03)
        self.assertEqual(round(N.next_event_date, 5), 0.03604)
        N.finish_service()
        self.assertEqual([str(obs) for obs in N.individuals], ['Individual 1', 'Individual 3'])

    def test_change_customer_class_method(self):
        seed(14)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_dynamic_classes/parameters.yml'))
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

    def test_block_individual_method(self):
        seed(4)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_deadlock_sim/parameters.yml'))
        inds = [ciw.Individual(i+1) for i in range(7)]
        N1 = Q.transitive_nodes[0]
        N1.individuals = inds[:6]
        N2 = Q.transitive_nodes[1]
        N2.accept(inds[6], 2)
        self.assertEqual(inds[6].is_blocked, False)
        self.assertEqual(N1.blocked_queue, [])
        self.assertEqual(Q.digraph.edges(), [])
        N2.block_individual(inds[6], N1)
        self.assertEqual(inds[6].is_blocked, True)
        [(2, 7)]
        self.assertEqual(Q.digraph.edges(), [('Server 1 at Node 2', 'Server 2 at Node 1'), ('Server 1 at Node 2', 'Server 1 at Node 1')])

    def test_release_method(self):
        seed(4)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        N = Q.transitive_nodes[0]
        inds = [ciw.Individual(i+1) for i in range(3)]
        for current_time in [0.01, 0.02, 0.03]:
            N.accept(inds[int(current_time*100 - 1)], current_time)
        self.assertEqual([str(obs) for obs in N.individuals], ['Individual 1', 'Individual 2', 'Individual 3'])
        N.update_next_event_date(0.03)
        self.assertEqual(round(N.next_event_date, 5), 0.03604)
        N.individuals[1].exit_date = 0.04  # shouldn't affect the next event date
        N.update_next_event_date(N.next_event_date+0.00001)
        self.assertEqual(round(N.next_event_date, 5), 0.03708)
        N.release(1, Q.transitive_nodes[1], N.next_event_date)
        self.assertEqual([str(obs) for obs in N.individuals], ['Individual 1', 'Individual 3'])
        N.update_next_event_date(N.next_event_date+0.00001)
        self.assertEqual(round(N.next_event_date, 5), 0.06447)

    def test_begin_service_if_possible_release_method(self):
        seed(50)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_deadlock_sim/parameters.yml'))
        inds = [ciw.Individual(i) for i in range(30)]
        Q.transitive_nodes[0].individuals = inds
        ind = Q.transitive_nodes[0].individuals[Q.transitive_nodes[0].c - 1]
        ind.service_time = 3.14
        ind.arrival_date = 100.0
        self.assertEqual(Q.digraph.nodes(), ['Server 2 at Node 1', 'Server 1 at Node 2', 'Server 1 at Node 1'])
        self.assertEqual(ind.arrival_date, 100.0)
        self.assertEqual(ind.service_time, 3.14)
        self.assertEqual(ind.service_start_date, False)
        self.assertEqual(ind.service_end_date, False)
        Q.transitive_nodes[0].begin_service_if_possible_release(200.0)
        self.assertEqual(ind.arrival_date, 100.0)
        self.assertEqual(round(ind.service_time,5), 3.14)
        self.assertEqual(ind.service_start_date, 200.0)
        self.assertEqual(round(ind.service_end_date,5), 203.14)

    def test_release_blocked_individual_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_deadlock_sim/parameters.yml'))
        N1 = Q.transitive_nodes[0]
        N2 = Q.transitive_nodes[1]
        N1.individuals = [ciw.Individual(i) for i in range(N1.c + 3)]
        N2.individuals = [ciw.Individual(i + 100) for i in range(N2.c + 4)]
        for ind in N1.individuals[:2]:
            N1.attach_server(N1.find_free_server(), ind)
        for ind in N2.individuals[:1]:
            N2.attach_server(N2.find_free_server(), ind)

        self.assertEqual([str(obs) for obs in N1.individuals], ['Individual 0', 'Individual 1', 'Individual 2', 'Individual 3', 'Individual 4'])
        self.assertEqual([str(obs) for obs in N2.individuals], ['Individual 100', 'Individual 101', 'Individual 102', 'Individual 103', 'Individual 104'])
        N1.release_blocked_individual(100)
        self.assertEqual([str(obs) for obs in N1.individuals], ['Individual 0', 'Individual 1', 'Individual 2', 'Individual 3', 'Individual 4'])
        self.assertEqual([str(obs) for obs in N2.individuals], ['Individual 100', 'Individual 101', 'Individual 102', 'Individual 103', 'Individual 104'])

        N1.blocked_queue = [(1, 1), (2, 100)]
        rel_ind = N1.individuals.pop(0)
        N1.detatch_server(rel_ind.server, rel_ind)

        N1.release_blocked_individual(110)
        self.assertEqual([str(obs) for obs in N1.individuals], ['Individual 2', 'Individual 3', 'Individual 4', 'Individual 100', 'Individual 1'])
        self.assertEqual([str(obs) for obs in N2.individuals], ['Individual 101', 'Individual 102', 'Individual 103', 'Individual 104'])

    def test_change_state_release_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        Q.state = [[0, 0], [0, 0], [2, 1], [0, 0]]
        N = Q.transitive_nodes[2]
        inds = [ciw.Individual(i) for i in range(3)]
        N.individuals = inds
        N.change_state_release(inds[0])
        self.assertEqual(Q.state, [[0, 0], [0, 0], [1, 1], [0, 0]])
        inds[1].is_blocked = True
        N.change_state_release(inds[1])
        self.assertEqual(Q.state, [[0, 0], [0, 0], [1, 0], [0, 0]])

    def test_change_state_block_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        Q.state = [[0, 0], [0, 0], [2, 1], [0, 0]]
        N = Q.transitive_nodes[2]
        N.change_state_block()
        self.assertEqual(Q.state, [[0, 0], [0, 0], [1, 2], [0, 0]])
        N.change_state_block()
        self.assertEqual(Q.state, [[0, 0], [0, 0], [0, 3], [0, 0]])

    def test_change_state_accept_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        Q.state = [[0, 0], [0, 0], [2, 1], [0, 0]]
        N = Q.transitive_nodes[2]
        N.change_state_accept()
        self.assertEqual(Q.state, [[0, 0], [0, 0], [3, 1], [0, 0]])
        N.change_state_accept()
        self.assertEqual(Q.state, [[0, 0], [0, 0], [4, 1], [0, 0]])

    def test_accept_method(self):
        seed(6)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        N = Q.transitive_nodes[0]
        N.next_event_date = 0.0
        self.assertEqual(N.individuals, [])
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

        N.accept(ind1, 0.01)
        self.assertEqual([str(obs) for obs in N.individuals], ['Individual 1'])
        self.assertEqual(ind1.arrival_date, 0.01)
        self.assertEqual(ind1.service_start_date, 0.01)
        self.assertEqual(round(ind1.service_time, 5), 0.18695)
        self.assertEqual(round(ind1.service_end_date, 5), 0.19695)

        N.accept(ind2, 0.02)
        N.accept(ind3, 0.03)
        N.accept(ind4, 0.04)
        self.assertEqual([str(obs) for obs in N.individuals], ['Individual 1', 'Individual 2', 'Individual 3', 'Individual 4'])
        self.assertEqual(round(ind4.arrival_date, 5), 0.04)
        self.assertEqual(round(ind4.service_start_date, 5), 0.04)
        self.assertEqual(round(ind4.service_time, 5), 0.1637)
        self.assertEqual(round(ind4.service_end_date, 5), 0.2037)

        N.accept(ind5, 0.05)
        N.accept(ind6, 0.06)
        N.accept(ind7, 0.07)
        N.accept(ind8, 0.08)
        N.accept(ind9, 0.09)
        N.accept(ind10, 0.1)
        self.assertEqual([str(obs) for obs in N.individuals], ['Individual 1', 'Individual 2', 'Individual 3', 'Individual 4', 'Individual 5', 'Individual 6', 'Individual 7', 'Individual 8', 'Individual 9', 'Individual 10'])
        self.assertEqual(round(ind10.arrival_date, 5), 0.1)
        self.assertEqual(ind10.service_start_date, False)
        self.assertEqual(round(ind10.service_time, 5), 0.16534)

    def test_begin_service_if_possible_accept_method(self):
        seed(50)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_deadlock_sim/parameters.yml'))
        ind = ciw.Individual(1)
        self.assertEqual(Q.digraph.nodes(), ['Server 2 at Node 1', 'Server 1 at Node 2', 'Server 1 at Node 1'])
        self.assertEqual(ind.arrival_date, False)
        self.assertEqual(ind.service_time, False)
        self.assertEqual(ind.service_start_date, False)
        self.assertEqual(ind.service_end_date, False)
        Q.transitive_nodes[0].begin_service_if_possible_accept(ind, 300)
        self.assertEqual(ind.arrival_date, 300)
        self.assertEqual(round(ind.service_time,5), 0.03382)
        self.assertEqual(ind.service_start_date, 300)
        self.assertEqual(round(ind.service_end_date,5), 300.03382)

    def test_kill_server_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_server_schedule/parameters.yml'))
        N = Q.transitive_nodes[0]
        s = N.servers[0]
        self.assertEqual([str(obs) for obs in N.servers], ['Server 1 at Node 1'])
        N.kill_server(s)
        N.highest_id += 1
        self.assertEqual(N.servers, [])
        N.next_event_date = 30
        N.have_event()
        self.assertEqual([str(obs) for obs in N.servers], ['Server 2 at Node 1', 'Server 3 at Node 1'])
        ind = ciw.Individual(666)
        N.attach_server(N.servers[0], ind)
        N.servers[0].offduty = True
        self.assertEqual([obs.busy for obs in N.servers], [True, False])
        self.assertEqual([obs.offduty for obs in N.servers], [True, False])
        N.detatch_server(N.servers[0], ind)
        self.assertEqual([str(obs) for obs in N.servers], ['Server 3 at Node 1'])


    def test_add_new_server_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_server_schedule/parameters.yml'))
        N = Q.transitive_nodes[0]
        self.assertEqual([str(obs) for obs in N.servers], ['Server 1 at Node 1'])
        s_indx = 3
        N.add_new_server(s_indx,1)
        self.assertEqual([str(obs) for obs in N.servers], ['Server 1 at Node 1', 'Server 2 at Node 1', 'Server 3 at Node 1', 'Server 4 at Node 1'])


    def test_update_next_event_date_method(self):
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        N = Q.transitive_nodes[0]
        self.assertEqual(N.next_event_date, 'Inf')
        self.assertEqual(N.individuals, [])
        N.update_next_event_date(0.0)
        self.assertEqual(N.next_event_date, 'Inf')

        ind1 = ciw.Individual(1)
        ind1.arrival_date = 0.3
        ind1.service_time = 0.2
        ind1.service_end_date = 0.5
        N.next_event_date = 0.3
        N.individuals = [ind1]
        N.update_next_event_date(N.next_event_date+0.000001)
        self.assertEqual(N.next_event_date, 0.5)

        ind2 = ciw.Individual(2)
        ind2.arrival_date = 0.4
        ind2.service_time = 0.2
        ind2.service_end_date = 0.6
        ind2.exit_date = False

        N.individuals = [ind1, ind2]
        N.update_next_event_date(N.next_event_date+0.000001)
        self.assertEqual(N.next_event_date, 0.6)

        ind2.exit_date = 0.9  # shouldn't affect next_event_date

        N.update_next_event_date(N.next_event_date+0.000001)
        self.assertEqual(N.next_event_date, 'Inf')


        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_server_schedule/parameters.yml'))
        N = Q.transitive_nodes[0]
        self.assertEqual(N.next_event_date, 30)
        self.assertEqual(N.individuals, [])
        N.update_next_event_date(0.0)
        self.assertEqual(N.next_event_date, 30)

        ind1 = ciw.Individual(1)
        ind1.arrival_date = 0.3
        ind1.service_time = 0.2
        ind1.service_end_date = 0.5
        N.next_event_date = 0.3
        N.individuals = [ind1]
        N.update_next_event_date(N.next_event_date+0.000001)
        self.assertEqual(N.next_event_date, 0.5)

        N.update_next_event_date(N.next_event_date+0.000001)
        self.assertEqual(N.next_event_date, 30)

    def test_next_node_method(self):
        seed(6)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        node = Q.transitive_nodes[0]
        self.assertEqual(str(node.next_node(0)), 'Node 4')
        self.assertEqual(str(node.next_node(0)), 'Node 4')
        self.assertEqual(str(node.next_node(0)), 'Node 4')
        self.assertEqual(str(node.next_node(0)), 'Node 4')
        self.assertEqual(str(node.next_node(0)), 'Node 2')
        self.assertEqual(str(node.next_node(0)), 'Node 4')

        seed(54)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        node = Q.transitive_nodes[2]
        self.assertEqual(str(node.next_node(0)), 'Node 2')
        self.assertEqual(str(node.next_node(0)), 'Node 4')
        self.assertEqual(str(node.next_node(0)), 'Node 2')
        self.assertEqual(str(node.next_node(0)), 'Node 2')
        self.assertEqual(str(node.next_node(0)), 'Node 2')
        self.assertEqual(str(node.next_node(0)), 'Node 2')
        self.assertEqual(str(node.next_node(0)), 'Node 4')
        self.assertEqual(str(node.next_node(0)), 'Node 2')

    def test_write_individual_record_method(self):
        seed(7)
        Q = ciw.Simulation(ciw.load_parameters('ciw/tests/datafortesting/logs_test_for_simulation/parameters.yml'))
        N = Q.transitive_nodes[0]
        ind = ciw.Individual(6)
        N.accept(ind, 3)
        ind.service_start_date = 3.5
        ind.exit_date = 9
        N.write_individual_record(ind)
        self.assertEqual(ind.data_records[1][0].arrival_date, 3)
        self.assertEqual(ind.data_records[1][0].wait, 0.5)
        self.assertEqual(ind.data_records[1][0].service_start_date, 3.5)
        self.assertEqual(round(ind.data_records[1][0].service_time, 5), 0.07894)
        self.assertEqual(round(ind.data_records[1][0].service_end_date, 5), 3.57894)
        self.assertEqual(round(ind.data_records[1][0].blocked, 5), 5.42106)
        self.assertEqual(ind.data_records[1][0].exit_date, 9)
        self.assertEqual(ind.data_records[1][0].customer_class, 0)


