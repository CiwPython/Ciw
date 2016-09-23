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
        N.servers[1].busy = True
        N.servers[2].busy = True
        self.assertEqual([obs.busy for obs in N.servers],
            [False, True, True, False])
        self.assertEqual([obs.offduty for obs in N.servers],
            [False, False, False, False])
        N.take_servers_off_duty()
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 2 at Node 1', 'Server 3 at Node 1'])
        self.assertEqual([obs.busy for obs in N.servers], [True, True])
        self.assertEqual([obs.offduty for obs in N.servers], [True, True])

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
        N.add_new_servers(3)
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 1 at Node 1',
             'Server 2 at Node 1',
             'Server 3 at Node 1',
             'Server 4 at Node 1'])
        N.servers[1].busy = True
        N.servers[2].busy = True
        self.assertEqual([obs.busy for obs in N.servers],
            [False, True, True, False])
        self.assertEqual([obs.offduty for obs in N.servers],
            [False, False, False, False])
        N.take_servers_off_duty(preempt=True)
        self.assertEqual([str(obs) for obs in N.servers],[])
        self.assertEqual([obs.busy for obs in N.servers], [])
        self.assertEqual([obs.offduty for obs in N.servers], [])
