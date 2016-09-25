import unittest
import ciw

class TestScheduling(unittest.TestCase):

    def test_change_shift_method(self):
        Q = ciw.Simulation(ciw.create_network(
            'ciw/tests/testing_parameters/params_schedule.yml'))
        N = Q.transitive_nodes[0]
        N.next_event_date = 30
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 1 at Node 1'])
        self.assertEqual([obs.busy for obs in N.servers], [False])
        self.assertEqual([obs.offduty for obs in N.servers], [False])
        self.assertEqual(N.c, 1)
        N.change_shift()
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 2 at Node 1', 'Server 3 at Node 1'])
        self.assertEqual([obs.busy for obs in N.servers], [False, False])
        self.assertEqual([obs.offduty for obs in N.servers], [False, False])
        self.assertEqual(N.c, 2)

        N.servers[0].busy = True
        N.next_event_date = 90
        N.change_shift()
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 2 at Node 1',
             'Server 4 at Node 1',
             'Server 5 at Node 1',
             'Server 6 at Node 1'])
        self.assertEqual([obs.busy for obs in N.servers],
            [True, False, False, False])
        self.assertEqual([obs.offduty for obs in N.servers],
            [True, False, False, False])
        self.assertEqual(N.c, 3)

    def test_take_servers_off_duty_method(self):
        Q = ciw.Simulation(ciw.create_network(
            'ciw/tests/testing_parameters/params_schedule.yml'))
        N = Q.transitive_nodes[0]
        N.add_new_servers(3)
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 1 at Node 1',
             'Server 2 at Node 1',
             'Server 3 at Node 1',
             'Server 4 at Node 1'])
        ind1 = ciw.Individual(5, 1)
        ind1.service_time = 5.5
        ind1.service_end_date = 7895.876
        ind2 = ciw.Individual(2, 0)
        ind2.service_time = 7.2
        ind2.service_end_date = 0.4321
        N.attach_server(N.servers[1], ind1)
        N.attach_server(N.servers[2], ind2)

        self.assertEqual([obs.busy for obs in N.servers],
            [False, True, True, False])
        self.assertEqual([obs.offduty for obs in N.servers],
            [False, False, False, False])
        self.assertEqual(ind1.service_time, 5.5)
        self.assertEqual(ind1.service_end_date, 7895.876)
        self.assertEqual(ind2.service_time, 7.2)
        self.assertEqual(ind2.service_end_date, 0.4321)

        N.take_servers_off_duty()
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 2 at Node 1', 'Server 3 at Node 1'])
        self.assertEqual([obs.busy for obs in N.servers], [True, True])
        self.assertEqual([obs.offduty for obs in N.servers], [True, True])
        self.assertEqual(ind1.service_time, 5.5)
        self.assertEqual(ind1.service_end_date, 7895.876)
        self.assertEqual(ind2.service_time, 7.2)
        self.assertEqual(ind2.service_end_date, 0.4321)

        self.assertEqual(N.interrupted_individuals, [])

    def test_check_if_shiftchange_method(self):
        Q = ciw.Simulation(ciw.create_network(
            'ciw/tests/testing_parameters/params_schedule.yml'))
        N = Q.transitive_nodes[0]
        N.next_event_date = 12.0
        self.assertEqual(N.check_if_shiftchange(), False)
        N.next_event_date = 30.0
        self.assertEqual(N.check_if_shiftchange(), True)

        Q = ciw.Simulation(ciw.create_network(
            'ciw/tests/testing_parameters/params.yml'))
        N = Q.transitive_nodes[0]
        N.next_event_date = 12.0
        self.assertEqual(N.check_if_shiftchange(), False)
        N.next_event_date = 30.0
        self.assertEqual(N.check_if_shiftchange(), False)


    def test_kill_server_method(self):
        Q = ciw.Simulation(ciw.create_network(
            'ciw/tests/testing_parameters/params_schedule.yml'))
        N = Q.transitive_nodes[0]
        s = N.servers[0]
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 1 at Node 1'])
        N.kill_server(s)
        self.assertEqual(N.servers, [])
        N.next_event_date = 30
        N.have_event()
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 2 at Node 1', 'Server 3 at Node 1'])
        ind = ciw.Individual(666)
        N.attach_server(N.servers[0], ind)
        N.servers[0].offduty = True
        self.assertEqual([obs.busy for obs in N.servers],
            [True, False])
        self.assertEqual([obs.offduty for obs in N.servers],
            [True, False])
        N.detatch_server(N.servers[0], ind)
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 3 at Node 1'])

    def test_add_new_servers_method(self):
        Q = ciw.Simulation(ciw.create_network(
            'ciw/tests/testing_parameters/params_schedule.yml'))
        N = Q.transitive_nodes[0]
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 1 at Node 1'])
        s_indx = 3
        N.add_new_servers(s_indx)
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 1 at Node 1',
             'Server 2 at Node 1',
             'Server 3 at Node 1',
             'Server 4 at Node 1'])


    def test_take_servers_off_duty_preempt_method(self):
        Q = ciw.Simulation(ciw.create_network(
            'ciw/tests/testing_parameters/params_schedule.yml'))
        N = Q.transitive_nodes[0]
        N.preempt = True
        N.add_new_servers(3)
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 1 at Node 1',
             'Server 2 at Node 1',
             'Server 3 at Node 1',
             'Server 4 at Node 1'])
        ind1 = ciw.Individual(5, 1, 1)
        ind1.service_time = 5.5
        ind1.arrival_date = 10
        ind1.service_end_date = 7895.876
        ind3 = ciw.Individual(7, 1, 1)
        ind3.service_time = 5.5
        ind3.arrival_date = 8
        ind3.service_end_date = 8895.876
        ind2 = ciw.Individual(2, 0, 0)
        ind2.service_time = 7.2
        ind2.arrival_date = 26
        ind2.service_end_date = 0.4321
        N.attach_server(N.servers[1], ind1)
        N.attach_server(N.servers[3], ind3)
        N.attach_server(N.servers[2], ind2)
        N.individuals = [[ind2], [ind3, ind1]]

        self.assertEqual([obs.busy for obs in N.servers],
            [False, True, True, True])
        self.assertEqual([obs.offduty for obs in N.servers],
            [False, False, False, False])
        self.assertEqual(ind1.service_time, 5.5)
        self.assertEqual(ind1.service_end_date, 7895.876)
        self.assertEqual(ind2.service_time, 7.2)
        self.assertEqual(ind2.service_end_date, 0.4321)
        N.take_servers_off_duty()
        self.assertEqual([str(obs) for obs in N.servers], [])
        self.assertEqual([obs.busy for obs in N.servers], [])
        self.assertEqual([obs.offduty for obs in N.servers], [])
        self.assertEqual(ind1.service_time, None)
        self.assertEqual(ind1.service_end_date, None)
        self.assertEqual(ind2.service_time, None)
        self.assertEqual(ind2.service_end_date, None)
        self.assertEqual(N.interrupted_individuals, [ind2, ind3, ind1])
        self.assertTrue(ind1 in N.individuals[1])
        self.assertTrue(ind3 in N.individuals[1])
        self.assertTrue(ind2 in N.individuals[0])



    def test_full_preemptive_simulation(self):
        params = {
            'Arrival_distributions': [['Deterministic', 7.0]],
            'Service_distributions': [['Deterministic', 5.0]],
            'Transition_matrices': [[0.0]],
            'ourschedule': ([[13, 1], [14, 0], [100, 2]], True),
            'Number_of_servers': ['ourschedule']
        }
        N = ciw.create_network(params)
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(14.5)

        self.assertEqual(len(Q.nodes[1].interrupted_individuals), 1)
        self.assertEqual(len(Q.nodes[1].all_individuals), 1)