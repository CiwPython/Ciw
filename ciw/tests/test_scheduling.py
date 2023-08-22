import unittest
import ciw
from decimal import Decimal

N_schedule = ciw.create_network(
    arrival_distributions={
        "Class 0": [ciw.dists.Exponential(0.05), ciw.dists.Exponential(0.04)],
        "Class 1": [ciw.dists.Exponential(0.04), ciw.dists.Exponential(0.06)],
    },
    number_of_servers=[[[1, 30], [2, 60], [1, 90], [3, 100]], 3],
    queue_capacities=[float("Inf"), 10],
    service_distributions={
        "Class 0": [ciw.dists.Deterministic(5.0), ciw.dists.Exponential(0.2)],
        "Class 1": [ciw.dists.Deterministic(10.0), ciw.dists.Exponential(0.1)],
    },
    routing={"Class 0": [[0.8, 0.1], [0.0, 0.0]], "Class 1": [[0.8, 0.1], [0.2, 0.0]]},
)


class TestScheduling(unittest.TestCase):
    def test_change_shift_method(self):
        Q = ciw.Simulation(N_schedule)
        N = Q.transitive_nodes[0]
        N.next_event_date = 30
        self.assertEqual([str(obs) for obs in N.servers], ["Server 1 at Node 1"])
        self.assertEqual([obs.busy for obs in N.servers], [False])
        self.assertEqual([obs.offduty for obs in N.servers], [False])
        self.assertEqual(N.c, 1)
        N.change_shift()
        self.assertEqual(
            [str(obs) for obs in N.servers],
            ["Server 2 at Node 1", "Server 3 at Node 1"],
        )
        self.assertEqual([obs.busy for obs in N.servers], [False, False])
        self.assertEqual([obs.offduty for obs in N.servers], [False, False])
        self.assertEqual(N.c, 2)

        N.servers[0].busy = True
        N.next_event_date = 90
        N.change_shift()
        self.assertEqual(
            [str(obs) for obs in N.servers],
            [
                "Server 2 at Node 1",
                "Server 4 at Node 1",
                "Server 5 at Node 1",
                "Server 6 at Node 1",
            ],
        )
        self.assertEqual([obs.busy for obs in N.servers], [True, False, False, False])
        self.assertEqual([obs.offduty for obs in N.servers], [True, False, False, False])
        self.assertEqual(N.c, 3)

    def test_take_servers_off_duty_method(self):
        Q = ciw.Simulation(N_schedule)
        N = Q.transitive_nodes[0]
        N.add_new_servers(3)
        self.assertEqual(
            [str(obs) for obs in N.servers],
            [
                "Server 1 at Node 1",
                "Server 2 at Node 1",
                "Server 3 at Node 1",
                "Server 4 at Node 1",
            ],
        )
        ind1 = ciw.Individual(5, 1)
        ind1.service_time = 5.5
        ind1.service_end_date = 7895.876
        ind2 = ciw.Individual(2, 0)
        ind2.service_time = 7.2
        ind2.service_end_date = 0.4321
        N.attach_server(N.servers[1], ind1)
        N.attach_server(N.servers[2], ind2)

        self.assertEqual([obs.busy for obs in N.servers], [False, True, True, False])
        self.assertEqual([obs.offduty for obs in N.servers], [False, False, False, False])
        self.assertEqual(ind1.service_time, 5.5)
        self.assertEqual(ind1.service_end_date, 7895.876)
        self.assertEqual(ind2.service_time, 7.2)
        self.assertEqual(ind2.service_end_date, 0.4321)

        N.take_servers_off_duty()
        self.assertEqual(
            [str(obs) for obs in N.servers],
            ["Server 2 at Node 1", "Server 3 at Node 1"],
        )
        self.assertEqual([obs.busy for obs in N.servers], [True, True])
        self.assertEqual([obs.offduty for obs in N.servers], [True, True])
        self.assertEqual(ind1.service_time, 5.5)
        self.assertEqual(ind1.service_end_date, 7895.876)
        self.assertEqual(ind2.service_time, 7.2)
        self.assertEqual(ind2.service_end_date, 0.4321)
        self.assertEqual(N.interrupted_individuals, [])


    def test_kill_server_method(self):
        Q = ciw.Simulation(N_schedule)
        N = Q.transitive_nodes[0]
        s = N.servers[0]
        self.assertEqual([str(obs) for obs in N.servers], ["Server 1 at Node 1"])
        N.kill_server(s)
        self.assertEqual(N.servers, [])
        N.next_event_date = 30
        N.next_event_type = "shift_change"
        N.have_event()
        self.assertEqual(
            [str(obs) for obs in N.servers],
            ["Server 2 at Node 1", "Server 3 at Node 1"],
        )
        ind = ciw.Individual(666)
        N.attach_server(N.servers[0], ind)
        N.servers[0].offduty = True
        self.assertEqual([obs.busy for obs in N.servers], [True, False])
        self.assertEqual([obs.offduty for obs in N.servers], [True, False])
        N.detatch_server(N.servers[0], ind)
        self.assertEqual([str(obs) for obs in N.servers], ["Server 3 at Node 1"])

    def test_add_new_servers_method(self):
        Q = ciw.Simulation(N_schedule)
        N = Q.transitive_nodes[0]
        self.assertEqual([str(obs) for obs in N.servers], ["Server 1 at Node 1"])
        N.add_new_servers(3)
        self.assertEqual(
            [str(obs) for obs in N.servers],
            [
                "Server 1 at Node 1",
                "Server 2 at Node 1",
                "Server 3 at Node 1",
                "Server 4 at Node 1",
            ],
        )
        N.add_new_servers(2)
        self.assertEqual(
            [str(obs) for obs in N.servers],
            [
                "Server 1 at Node 1",
                "Server 2 at Node 1",
                "Server 3 at Node 1",
                "Server 4 at Node 1",
                "Server 5 at Node 1",
                "Server 6 at Node 1",
            ],
        )
        N.add_new_servers(10)
        self.assertEqual(
            [str(obs) for obs in N.servers],
            [
                "Server 1 at Node 1",
                "Server 2 at Node 1",
                "Server 3 at Node 1",
                "Server 4 at Node 1",
                "Server 5 at Node 1",
                "Server 6 at Node 1",
                "Server 7 at Node 1",
                "Server 8 at Node 1",
                "Server 9 at Node 1",
                "Server 10 at Node 1",
                "Server 11 at Node 1",
                "Server 12 at Node 1",
                "Server 13 at Node 1",
                "Server 14 at Node 1",
                "Server 15 at Node 1",
                "Server 16 at Node 1",
            ],
        )

    def test_take_servers_off_duty_preempt_method(self):
        Q = ciw.Simulation(N_schedule)
        N = Q.transitive_nodes[0]
        N.schedule_preempt = "resample"
        N.add_new_servers(3)
        self.assertEqual(
            [str(obs) for obs in N.servers],
            [
                "Server 1 at Node 1",
                "Server 2 at Node 1",
                "Server 3 at Node 1",
                "Server 4 at Node 1",
            ],
        )
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

        self.assertEqual([obs.busy for obs in N.servers], [False, True, True, True])
        self.assertEqual([obs.offduty for obs in N.servers], [False, False, False, False])
        self.assertEqual(ind1.service_time, 5.5)
        self.assertEqual(ind1.service_end_date, 7895.876)
        self.assertEqual(ind2.service_time, 7.2)
        self.assertEqual(ind2.service_end_date, 0.4321)
        N.take_servers_off_duty()
        self.assertEqual([str(obs) for obs in N.servers], [])
        self.assertEqual([obs.busy for obs in N.servers], [])
        self.assertEqual([obs.offduty for obs in N.servers], [])
        self.assertEqual(ind1.service_time, "resample")
        self.assertEqual(ind1.original_service_time, 5.5)
        self.assertEqual(ind1.service_end_date, False)
        self.assertEqual(ind2.service_time, "resample")
        self.assertEqual(ind2.original_service_time, 7.2)
        self.assertEqual(ind2.service_end_date, False)
        self.assertEqual(N.interrupted_individuals, [ind2, ind3, ind1])
        self.assertTrue(ind1 in N.individuals[1])
        self.assertTrue(ind3 in N.individuals[1])
        self.assertTrue(ind2 in N.individuals[0])

    def test_full_preemptive_simulation(self):
        # Run until an individal gets interrupted
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(7.0)],
            service_distributions=[ciw.dists.Deterministic(5.0)],
            routing=[[0.0]],
            number_of_servers=[([[1, 15], [0, 17], [2, 100]], "resample")],
        )
        Q = ciw.Simulation(N)

        self.assertTrue(Q.nodes[1].schedule_preempt)

        Q.simulate_until_max_time(15.5)

        self.assertEqual(len(Q.nodes[1].interrupted_individuals), 1)
        self.assertEqual(len(Q.nodes[1].all_individuals), 1)
        self.assertEqual(Q.nodes[1].all_individuals, Q.nodes[1].interrupted_individuals)
        interrupted_ind = Q.nodes[1].interrupted_individuals[0]
        self.assertEqual(interrupted_ind.arrival_date, 14.0)
        self.assertEqual(interrupted_ind.service_start_date, False)
        self.assertEqual(interrupted_ind.service_time, "resample")
        self.assertEqual(interrupted_ind.original_service_time, 5.0)
        self.assertEqual(interrupted_ind.time_left, 4.0)
        self.assertEqual(interrupted_ind.service_end_date, False)

        # Run until interrupted individual finishes service
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(7.0)],
            service_distributions=[ciw.dists.Deterministic(5.0)],
            routing=[[0.0]],
            number_of_servers=[([[1, 15], [0, 17], [2, 100]], "continue")],
        )
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
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(3.0)],
            service_distributions=[ciw.dists.Deterministic(10.0)],
            routing=[[0.0]],
            number_of_servers=[([[4, 12.5], [0, 17], [1, 100]], "continue")],
        )
        Q = ciw.Simulation(N)
        self.assertTrue(Q.nodes[1].schedule_preempt)

        Q.simulate_until_max_time(27.5)
        recs = Q.get_all_records(only=["service"])
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
            number_of_servers=[([[3, 7.0], [2, 11.0], [1, 20.0]], False)],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(19.0)

        nd = Q.transitive_nodes[0]
        self.assertEqual(nd.overtime, [0.0, 1.0, 3.0, 2.0, 3.0])
        self.assertEqual(sum(nd.overtime) / len(nd.overtime), 1.8)

    def test_overtime_exact(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1.0, 0.0, 0.0, 8.0, 0.0, 3.0, 10000.0])],
            service_distributions=[ciw.dists.Sequential([5.0, 7.0, 9.0, 4.0, 5.0, 5.0])],
            number_of_servers=[([[3, 7.0], [2, 11.0], [1, 20.0]], False)],
        )
        Q = ciw.Simulation(N, exact=26)
        Q.simulate_until_max_time(19.0)

        nd = Q.transitive_nodes[0]
        self.assertEqual(
            nd.overtime,
            [
                Decimal("0.0"),
                Decimal("1.0"),
                Decimal("3.0"),
                Decimal("2.0"),
                Decimal("3.0"),
            ],
        )
        self.assertEqual(sum(nd.overtime) / len(nd.overtime), Decimal("1.8"))

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
            number_of_servers=[([[1, 5], [0, 9], [1, 100]], "restart")],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(40)
        recs = Q.get_all_records(only=["service"])
        r1 = recs[0]
        self.assertEqual(r1.arrival_date, 1)
        self.assertEqual(r1.service_start_date, 9)
        self.assertEqual(r1.service_end_date, 19)
        self.assertEqual(r1.service_time, 10)
        self.assertEqual(r1.waiting_time, 8)

        # Testing under continue
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1, float("inf")])],
            service_distributions=[ciw.dists.Sequential([10, 20])],
            number_of_servers=[([[1, 5], [0, 9], [1, 100]], "continue")],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(40)
        recs = Q.get_all_records(only=["service"])
        r1 = recs[0]
        self.assertEqual(r1.arrival_date, 1)
        self.assertEqual(r1.service_start_date, 9)
        self.assertEqual(r1.service_end_date, 15)
        self.assertEqual(r1.service_time, 6)
        self.assertEqual(r1.waiting_time, 8)

        # Testing under resample
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1, float("inf")])],
            service_distributions=[ciw.dists.Sequential([10, 20])],
            number_of_servers=[([[1, 5], [0, 9], [1, 100]], "resample")],
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(40)
        recs = Q.get_all_records(only=["service"])
        r1 = recs[0]
        self.assertEqual(r1.arrival_date, 1)
        self.assertEqual(r1.service_start_date, 9)
        self.assertEqual(r1.service_end_date, 29)
        self.assertEqual(r1.service_time, 20)
        self.assertEqual(r1.waiting_time, 8)

    def test_priority_preemption_when_zero_servers(self):
        """
        Test whether pre-emptive priorities and server schedules where there are zero servers work well together.

        We will show two scenarios.
            - The first where the one server goes off and back on duty while there are no customers present.
            - The second where the server goes off duty but back on duty while there are customers waiting.
        """
        # First scenario
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Deterministic(7)],
                "Class 1": [ciw.dists.Deterministic(13)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(5.5)],
                "Class 1": [ciw.dists.Deterministic(1.5)],
            },
            number_of_servers=[[[1, 20.3], [0, 20.6], [1, 100]]],
            priority_classes=({"Class 0": 1, "Class 1": 0}, ["continue"]),
        )

        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(35)

        recs = Q.get_all_records()
        # Individual 1
        self.assertEqual(recs[0].id_number, 1)
        self.assertEqual(recs[0].customer_class, 'Class 0')
        self.assertEqual(recs[0].arrival_date, 7)
        self.assertEqual(recs[0].service_start_date, 7)
        self.assertEqual(recs[0].service_end_date, 12.5)
        self.assertEqual(recs[0].record_type, "service")
        # Individual 2
        self.assertEqual(recs[1].id_number, 2)
        self.assertEqual(recs[1].customer_class, 'Class 1')
        self.assertEqual(recs[1].arrival_date, 13)
        self.assertEqual(recs[1].service_start_date, 13)
        self.assertEqual(recs[1].service_end_date, 14.5)
        self.assertEqual(recs[1].record_type, "service")
        # Individual 3
        self.assertEqual(recs[2].id_number, 3)
        self.assertEqual(recs[2].customer_class, 'Class 0')
        self.assertEqual(recs[2].arrival_date, 14)
        self.assertEqual(recs[2].service_start_date, 14.5)
        self.assertEqual(recs[2].service_end_date, 20)
        self.assertEqual(recs[2].record_type, "service")
        # Individual 5
        self.assertEqual(recs[3].id_number, 5)
        self.assertEqual(recs[3].customer_class, 'Class 1')
        self.assertEqual(recs[3].arrival_date, 26)
        self.assertEqual(recs[3].service_start_date, 26)
        self.assertEqual(recs[3].service_end_date, 27.5)
        self.assertEqual(recs[3].record_type, "service")
        # Individual 4's interrupted service
        self.assertEqual(recs[4].id_number, 4)
        self.assertEqual(recs[4].customer_class, 'Class 0')
        self.assertEqual(recs[4].arrival_date, 21)
        self.assertEqual(recs[4].service_start_date, 21)
        self.assertEqual(recs[4].record_type, "interrupted service")
        # Individual 4's resumed service
        self.assertEqual(recs[5].id_number, 4)
        self.assertEqual(recs[5].customer_class, 'Class 0')
        self.assertEqual(recs[5].arrival_date, 21)
        self.assertEqual(recs[5].service_start_date, 27.5)
        self.assertEqual(recs[5].service_end_date, 28)
        self.assertEqual(recs[5].record_type, "service")
        # Individual 6
        self.assertEqual(recs[6].id_number, 6)
        self.assertEqual(recs[6].customer_class, 'Class 0')
        self.assertEqual(recs[6].arrival_date, 28)
        self.assertEqual(recs[6].service_start_date, 28)
        self.assertEqual(recs[6].service_end_date, 33.5)
        self.assertEqual(recs[6].record_type, "service")

        # Second scenario
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Deterministic(7)],
                "Class 1": [ciw.dists.Deterministic(13)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Deterministic(5.5)],
                "Class 1": [ciw.dists.Deterministic(1.5)],
            },
            number_of_servers=[[[1, 20.3], [0, 22], [1, 100]]],
            priority_classes=({"Class 0": 1, "Class 1": 0}, ["continue"]),
        )

        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(35)

        recs = Q.get_all_records()
        # Individual 1
        self.assertEqual(recs[0].id_number, 1)
        self.assertEqual(recs[0].customer_class, 'Class 0')
        self.assertEqual(recs[0].arrival_date, 7)
        self.assertEqual(recs[0].service_start_date, 7)
        self.assertEqual(recs[0].service_end_date, 12.5)
        self.assertEqual(recs[0].record_type, "service")
        # Individual 2
        self.assertEqual(recs[1].id_number, 2)
        self.assertEqual(recs[1].customer_class, 'Class 1')
        self.assertEqual(recs[1].arrival_date, 13)
        self.assertEqual(recs[1].service_start_date, 13)
        self.assertEqual(recs[1].service_end_date, 14.5)
        self.assertEqual(recs[1].record_type, "service")
        # Individual 3
        self.assertEqual(recs[2].id_number, 3)
        self.assertEqual(recs[2].customer_class, 'Class 0')
        self.assertEqual(recs[2].arrival_date, 14)
        self.assertEqual(recs[2].service_start_date, 14.5)
        self.assertEqual(recs[2].service_end_date, 20)
        self.assertEqual(recs[2].record_type, "service")
        # Individual 5
        self.assertEqual(recs[3].id_number, 5)
        self.assertEqual(recs[3].customer_class, 'Class 1')
        self.assertEqual(recs[3].arrival_date, 26)
        self.assertEqual(recs[3].service_start_date, 26)
        self.assertEqual(recs[3].service_end_date, 27.5)
        self.assertEqual(recs[3].record_type, "service")
        # Individual 4's interrupted service
        self.assertEqual(recs[4].id_number, 4)
        self.assertEqual(recs[4].customer_class, 'Class 0')
        self.assertEqual(recs[4].arrival_date, 21)
        self.assertEqual(recs[4].service_start_date, 22)
        self.assertEqual(recs[4].record_type, "interrupted service")
        # Individual 4's resumed service
        self.assertEqual(recs[5].id_number, 4)
        self.assertEqual(recs[5].customer_class, 'Class 0')
        self.assertEqual(recs[5].arrival_date, 21)
        self.assertEqual(recs[5].service_start_date, 27.5)
        self.assertEqual(recs[5].service_end_date, 29)
        self.assertEqual(recs[5].record_type, "service")
        # Individual 6
        self.assertEqual(recs[6].id_number, 6)
        self.assertEqual(recs[6].customer_class, 'Class 0')
        self.assertEqual(recs[6].arrival_date, 28)
        self.assertEqual(recs[6].service_start_date, 29)
        self.assertEqual(recs[6].service_end_date, 34.5)
        self.assertEqual(recs[6].record_type, "service")
