import unittest
import ciw
from decimal import Decimal


class TestScheduling(unittest.TestCase):
    def test_change_shift_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
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
        Q = ciw.Simulation(ciw.create_network_from_yml(
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
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_schedule.yml'))
        N = Q.transitive_nodes[0]
        N.next_event_date = 12.0
        self.assertEqual(N.check_if_shiftchange(), False)
        N.next_event_date = 30.0
        self.assertEqual(N.check_if_shiftchange(), True)

        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml'))
        N = Q.transitive_nodes[0]
        N.next_event_date = 12.0
        self.assertEqual(N.check_if_shiftchange(), False)
        N.next_event_date = 30.0
        self.assertEqual(N.check_if_shiftchange(), False)


    def test_kill_server_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
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
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_schedule.yml'))
        N = Q.transitive_nodes[0]
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 1 at Node 1'])
        N.add_new_servers(3)
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 1 at Node 1',
             'Server 2 at Node 1',
             'Server 3 at Node 1',
             'Server 4 at Node 1'])
        N.add_new_servers(2)
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 1 at Node 1',
             'Server 2 at Node 1',
             'Server 3 at Node 1',
             'Server 4 at Node 1',
             'Server 5 at Node 1',
             'Server 6 at Node 1'])
        N.add_new_servers(10)
        self.assertEqual([str(obs) for obs in N.servers],
            ['Server 1 at Node 1',
             'Server 2 at Node 1',
             'Server 3 at Node 1',
             'Server 4 at Node 1',
             'Server 5 at Node 1',
             'Server 6 at Node 1',
             'Server 7 at Node 1',
             'Server 8 at Node 1',
             'Server 9 at Node 1',
             'Server 10 at Node 1',
             'Server 11 at Node 1',
             'Server 12 at Node 1',
             'Server 13 at Node 1',
             'Server 14 at Node 1',
             'Server 15 at Node 1',
             'Server 16 at Node 1'])


    def test_take_servers_off_duty_preempt_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params_schedule.yml'))
        N = Q.transitive_nodes[0]
        N.schedule_preempt = 'resample'
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
        self.assertEqual(ind1.service_time, 'resample')
        self.assertEqual(ind1.original_service_time, 5.5)
        self.assertEqual(ind1.service_end_date, False)
        self.assertEqual(ind2.service_time, 'resample')
        self.assertEqual(ind2.original_service_time, 7.2)
        self.assertEqual(ind2.service_end_date, False)
        self.assertEqual(N.interrupted_individuals, [ind2, ind3, ind1])
        self.assertTrue(ind1 in N.individuals[1])
        self.assertTrue(ind3 in N.individuals[1])
        self.assertTrue(ind2 in N.individuals[0])



    def test_full_preemptive_simulation(self):
        # Run until an individal gets interrupted
        params = {
            'arrival_distributions': [ciw.dists.Deterministic(7.0)],
            'service_distributions': [ciw.dists.Deterministic(5.0)],
            'routing': [[0.0]],
            'number_of_servers': [([[1, 15], [0, 17], [2, 100]], 'resample')]
        }
        N = ciw.create_network(**params)
        Q = ciw.Simulation(N)

        self.assertTrue(Q.nodes[1].schedule_preempt)

        Q.simulate_until_max_time(15.5)

        self.assertEqual(len(Q.nodes[1].interrupted_individuals), 1)
        self.assertEqual(len(Q.nodes[1].all_individuals), 1)
        self.assertEqual(Q.nodes[1].all_individuals, Q.nodes[1].interrupted_individuals)
        interrupted_ind = Q.nodes[1].interrupted_individuals[0]
        self.assertEqual(interrupted_ind.arrival_date, 14.0)
        self.assertEqual(interrupted_ind.service_start_date, False)
        self.assertEqual(interrupted_ind.service_time, 'resample')
        self.assertEqual(interrupted_ind.original_service_time, 5.0)
        self.assertEqual(interrupted_ind.time_left, 4.0)
        self.assertEqual(interrupted_ind.service_end_date, False)


        # Run until interrupted individual finishes service
        params = {
            'arrival_distributions': [ciw.dists.Deterministic(7.0)],
            'service_distributions': [ciw.dists.Deterministic(5.0)],
            'routing': [[0.0]],
            'number_of_servers': [([[1, 15], [0, 17], [2, 100]], 'continue')]
        }
        N = ciw.create_network(**params)
        Q = ciw.Simulation(N)

        self.assertTrue(Q.nodes[1].schedule_preempt)

        Q.simulate_until_max_time(22.5)
        recs = Q.get_all_records()

        self.assertEqual(len(Q.nodes[1].interrupted_individuals), 0)
        self.assertEqual(len(Q.nodes[1].all_individuals), 1)
        self.assertEqual(set([r.service_time for r in recs]), set([5.0, 4.0]))
        # 5 due to the one individual who has finished service without interruption.
        # 4 due to the 1 time unit in service before interruption not counting.


        # Example where more customers are interrupted than can restart service
        params = {
            'arrival_distributions': [ciw.dists.Deterministic(3.0)],
            'service_distributions': [ciw.dists.Deterministic(10.0)],
            'routing': [[0.0]],
            'number_of_servers': [([[4, 12.5], [0, 17], [1, 100]], 'continue')]
        }
        N = ciw.create_network(**params)
        Q = ciw.Simulation(N)
        self.assertTrue(Q.nodes[1].schedule_preempt)

        Q.simulate_until_max_time(27.5)
        recs = Q.get_all_records()
        self.assertEqual(len(Q.nodes[1].interrupted_individuals), 1)
        self.assertEqual(len(Q.nodes[1].all_individuals), 7)
        self.assertEqual([r.service_time for r in recs], [0.5, 3.5])
        # 0.5 due to the individual beginning service at time 3, and first service
        # finishing at time 12.5 (total: 9.5 time units). Then there is only 0.5
        # units left and only the final part is counted here.
        # 3.5 due to the individual beginning service at time 6, and first service
        # finishing at time 12.5 (total: 6.5 time units). Then they only restart
        # once the first customer has finished their second service, at time 17.5,
        # and there are 3.5 time units left.


    def test_overtime(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1.0, 0.0, 0.0, 8.0, 0.0, 3.0, 10000.0])],
            service_distributions=[ciw.dists.Sequential([5.0, 7.0, 9.0, 4.0, 5.0, 5.0])],
            number_of_servers=[([[3, 7.0], [2, 11.0], [1, 20.0]], False)]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(19.0)

        nd = Q.transitive_nodes[0]
        self.assertEqual(nd.overtime, [0.0, 1.0, 3.0, 2.0, 3.0])
        self.assertEqual(sum(nd.overtime)/len(nd.overtime), 1.8)

    def test_overtime_exact(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1.0, 0.0, 0.0, 8.0, 0.0, 3.0, 10000.0])],
            service_distributions=[ciw.dists.Sequential([5.0, 7.0, 9.0, 4.0, 5.0, 5.0])],
            number_of_servers=[([[3, 7.0], [2, 11.0], [1, 20.0]], False)]
        )
        Q = ciw.Simulation(N, exact=26)
        Q.simulate_until_max_time(19.0)

        nd = Q.transitive_nodes[0]
        self.assertEqual(nd.overtime, [Decimal('0.0'), Decimal('1.0'), Decimal('3.0'), Decimal('2.0'), Decimal('3.0')])
        self.assertEqual(sum(nd.overtime)/len(nd.overtime), Decimal('1.8'))


    def test_preemptive_schedules_resume_options(self):
        """
        A customer arrives at date 1, who's service time alternates
        between service times of 10 and 20.

        Servers have a schedule, 1 server is on duty from the start, then 0
        servers are on duty from time 5 to 9, then 1 server is on duty again.

        The customer would be displaced at time 5. Then and would restart
        service at time 9. 
            - Under "restart" we would expect them to leave at time 19
            (service time = 10)
            - Under "continue" we would expect them to leave at time 15
            (service time = 10 - 4 = 6)
            - Under "resample" we would expect them to leave at time 29
            (service time = 20)
        """ 
        # Testing under restart
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1, float("inf")])],
            service_distributions=[ciw.dists.Sequential([10, 20])],
            number_of_servers=[([[1, 5], [0, 9], [1, 100]], 'restart')],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(40)
        recs = Q.get_all_records()
        r1 = [r for r in recs if r.record_type == "service"][0]
        self.assertEqual(r1.arrival_date, 1)
        self.assertEqual(r1.service_start_date, 9)
        self.assertEqual(r1.service_end_date, 19)
        self.assertEqual(r1.service_time, 10)
        self.assertEqual(r1.waiting_time, 8)

        # Testing under continue
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1, float("inf")])],
            service_distributions=[ciw.dists.Sequential([10, 20])],
            number_of_servers=[([[1, 5], [0, 9], [1, 100]], 'continue')],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(40)
        recs = Q.get_all_records()
        r1 = [r for r in recs if r.record_type == "service"][0]
        self.assertEqual(r1.arrival_date, 1)
        self.assertEqual(r1.service_start_date, 9)
        self.assertEqual(r1.service_end_date, 15)
        self.assertEqual(r1.service_time, 6)
        self.assertEqual(r1.waiting_time, 8)

        # Testing under resample
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1, float("inf")])],
            service_distributions=[ciw.dists.Sequential([10, 20])],
            number_of_servers=[([[1, 5], [0, 9], [1, 100]], 'resample')],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(40)
        recs = Q.get_all_records()
        r1 = [r for r in recs if r.record_type == "service"][0]
        self.assertEqual(r1.arrival_date, 1)
        self.assertEqual(r1.service_start_date, 9)
        self.assertEqual(r1.service_end_date, 29)
        self.assertEqual(r1.service_time, 20)
        self.assertEqual(r1.waiting_time, 8)
