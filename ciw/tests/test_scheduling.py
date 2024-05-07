import unittest
import ciw
from decimal import Decimal
from collections import Counter
import math

N_schedule = ciw.create_network(
    arrival_distributions={
        "Class 0": [ciw.dists.Exponential(0.05), ciw.dists.Exponential(0.04)],
        "Class 1": [ciw.dists.Exponential(0.04), ciw.dists.Exponential(0.06)],
    },
    number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 2, 1, 3], shift_end_dates=[30, 60, 90, 100]), 3],
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
        N.have_event()
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

        N.next_event_date = 60
        N.change_shift()
        self.assertEqual(
            [str(obs) for obs in N.servers],
            ["Server 4 at Node 1"]
        )

        N.servers[0].busy = True
        N.next_event_date = 90
        N.change_shift()
        self.assertEqual(
            [str(obs) for obs in N.servers],
            [
                "Server 4 at Node 1",
                "Server 5 at Node 1",
                "Server 6 at Node 1",
                "Server 7 at Node 1",
            ],
        )
        self.assertEqual([obs.busy for obs in N.servers], [True, False, False, False])
        self.assertEqual([obs.offduty for obs in N.servers], [True, False, False, False])
        self.assertEqual(N.c, 3)

    def test_take_servers_off_duty_method(self):
        Q = ciw.Simulation(N_schedule)
        N = Q.transitive_nodes[0]
        N.have_event()
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
        N.have_event()
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
        N.have_event()
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
        N = N_schedule
        N.service_centres[0].number_of_servers.preemption = 'resample'
        Q = ciw.Simulation(N)
        N = Q.transitive_nodes[0]
        N.have_event()
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
        N.take_servers_off_duty(preemption='resample')
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
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 0, 2], shift_end_dates=[15, 17, 100], preemption="resample")],
        )
        Q = ciw.Simulation(N)

        self.assertEqual(Q.nodes[1].schedule.preemption, 'resample')

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
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 0, 2], shift_end_dates=[15, 17, 100], preemption="resume")],
        )
        Q = ciw.Simulation(N)

        self.assertEqual(Q.nodes[1].schedule.preemption, 'resume')

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
            number_of_servers=[ciw.Schedule(numbers_of_servers=[4, 0, 1], shift_end_dates=[12.5, 17, 100], preemption="resume")],
        )
        Q = ciw.Simulation(N)
        self.assertEqual(Q.nodes[1].schedule.preemption, 'resume')

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
            number_of_servers=[ciw.Schedule(numbers_of_servers=[3, 2, 1], shift_end_dates=[7.0, 11.0, 20.0], preemption=False)],
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
            number_of_servers=[ciw.Schedule(numbers_of_servers=[3, 2, 1], shift_end_dates=[7.0, 11.0, 20.0], preemption=False)],
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
            - Under "resume" we would expect them to leave at time 15
            (service time = 10 - 4 = 6)
            - Under "resample" we would expect them to leave at time 29
            (service time = 20)
        """
        # Testing under restart
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1, float("inf")])],
            service_distributions=[ciw.dists.Sequential([10, 20])],
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 0, 1], shift_end_dates=[5, 9, 100], preemption="restart")],
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

        # Testing under resume
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1, float("inf")])],
            service_distributions=[ciw.dists.Sequential([10, 20])],
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 0, 1], shift_end_dates=[5, 9, 100], preemption="resume")],
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
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 0, 1], shift_end_dates=[5, 9, 100], preemption="resample")],
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
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 0, 1], shift_end_dates=[20.3, 20.6, 100])],
            priority_classes=({"Class 0": 1, "Class 1": 0}, ["resume"]),
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
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 0, 1], shift_end_dates=[20.3, 22, 100])],
            priority_classes=({"Class 0": 1, "Class 1": 0}, ["resume"]),
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

    def test_resuming_interruption_after_blockage(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([5, float('inf')]), ciw.dists.Sequential([1, float('inf')])],
            service_distributions=[ciw.dists.Deterministic(1), ciw.dists.Deterministic(9)],
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 0], shift_end_dates=[8, 200], preemption='resume'), 1],
            queue_capacities=[float('inf'), 0],
            routing=[[0.0, 1.0], [0.0, 0.0]]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(35)

        C1 = Q.nodes[-1].all_individuals[0]
        C2 = Q.nodes[-1].all_individuals[1]

        self.assertEqual(C1.id_number, 1)
        self.assertEqual(C1.data_records[0].node, 2)
        self.assertEqual(C1.data_records[0].arrival_date, 1)
        self.assertEqual(C1.data_records[0].service_start_date, 1)
        self.assertEqual(C1.data_records[0].waiting_time, 0)
        self.assertEqual(C1.data_records[0].service_end_date, 10)
        self.assertEqual(C1.data_records[0].exit_date, 10)
        self.assertEqual(C1.data_records[0].time_blocked, 0)

        self.assertEqual(C2.id_number, 2)
        self.assertEqual(C2.data_records[0].node, 1)
        self.assertEqual(C2.data_records[0].arrival_date, 5)
        self.assertEqual(C2.data_records[0].service_start_date, 5)
        self.assertEqual(C2.data_records[0].waiting_time, 0)
        self.assertEqual(C2.data_records[0].exit_date, 8)

        self.assertEqual(C2.data_records[1].node, 1)
        self.assertEqual(C2.data_records[1].arrival_date, 5)
        self.assertEqual(C2.data_records[1].service_start_date, 5)
        self.assertEqual(C2.data_records[1].waiting_time, 0)
        self.assertEqual(C2.data_records[1].service_end_date, 6)
        self.assertEqual(C2.data_records[1].exit_date, 10)
        self.assertEqual(C2.data_records[1].time_blocked, 4)

        self.assertEqual(C2.data_records[2].node, 2)
        self.assertEqual(C2.data_records[2].arrival_date, 10)
        self.assertEqual(C2.data_records[2].service_start_date, 10)
        self.assertEqual(C2.data_records[2].waiting_time, 0)
        self.assertEqual(C2.data_records[2].service_end_date, 19)
        self.assertEqual(C2.data_records[2].exit_date, 19)
        self.assertEqual(C2.data_records[2].time_blocked, 0)

    def test_slotted_object(self):
        S = ciw.Slotted(slots=[1, 2, 3, 4], slot_sizes=[3, 2, 5, 3])
        S.initialise()
        self.assertEqual((S.next_slot_date, S.slot_size), (1, 3))
        S.get_next_slot()
        self.assertEqual((S.next_slot_date, S.slot_size), (2, 2))
        S.get_next_slot()
        self.assertEqual((S.next_slot_date, S.slot_size), (3, 5))
        S.get_next_slot()
        self.assertEqual((S.next_slot_date, S.slot_size), (4, 3))
        S.get_next_slot()
        self.assertEqual((S.next_slot_date, S.slot_size), (5, 3))
        S.get_next_slot()
        self.assertEqual((S.next_slot_date, S.slot_size), (6, 2))
        S.get_next_slot()
        self.assertEqual((S.next_slot_date, S.slot_size), (7, 5))
        S.get_next_slot()
        self.assertEqual((S.next_slot_date, S.slot_size), (8, 3))
        S.get_next_slot()
        self.assertEqual((S.next_slot_date, S.slot_size), (9, 3))

    def test_slotted_services(self):
        """
        Arrivals occur at times [0.3, 0.5, 0.7, 1.2, 1.3, 1.8, 2.6, 2.7, 3.1]
        All services last 0.5 time units
        Services are slotted at times [1, 2, 3, 4]
        Slotted services have capacities [3, 2, 5, 3]
        """
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([0.3, 0.2, 0.2, 0.5, 0.1, 0.5, 0.8, 0.1, 0.4, float('inf')])],
            service_distributions=[ciw.dists.Deterministic(0.5)],
            number_of_servers=[ciw.Slotted(slots=[1, 2, 3, 4], slot_sizes=[3, 2, 5, 3])]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(5.6)
        recs = Q.get_all_records()
        recs = sorted(recs, key=lambda rec: rec.id_number)

        self.assertEqual(len(Q.nodes[-1].all_individuals), 9)

        expected_service_dates = [1, 1, 1, 2, 2, 3, 3, 3, 4]
        observed_service_dates = [r.service_start_date for r in recs]
        self.assertEqual(observed_service_dates, expected_service_dates)
        self.assertFalse(any([ind.server for ind in Q.nodes[-1].all_individuals]))

    def test_slotted_services_with_offset(self):
        """
        Arrivals occur at times [0.3, 0.5, 0.7, 1.2, 1.3, 1.8, 2.6, 2.7, 3.1]
        All services last 0.5 time units
        Services are slotted at times [1.05, 2.05, 3.05, 4.05]
        Slotted services have capacities [3, 2, 5, 3]
        """
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([0.3, 0.2, 0.2, 0.5, 0.1, 0.5, 0.8, 0.1, 0.4, float('inf')])],
            service_distributions=[ciw.dists.Deterministic(0.5)],
            number_of_servers=[ciw.Slotted(slots=[1, 2, 3, 4], slot_sizes=[3, 2, 5, 3], offset=0.05)]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(5.6)
        recs = Q.get_all_records()
        recs = sorted(recs, key=lambda rec: rec.id_number)

        self.assertEqual(len(Q.nodes[-1].all_individuals), 9)

        expected_service_dates = [1.05, 1.05, 1.05, 2.05, 2.05, 3.05, 3.05, 3.05, 4.05]
        observed_service_dates = [r.service_start_date for r in recs]
        self.assertEqual(observed_service_dates, expected_service_dates)
        self.assertFalse(any([ind.server for ind in Q.nodes[-1].all_individuals]))

    def test_slotted_services_repeat(self):
        """
        Arrivals occur at times [0.7, 1.4, 2.6, 2.9, 4.3, 5.5, 6.1, 15.0]
        All services last 0.2 time units
        Services are slotted at times [1.5, 4.4, 5.9, 8.8, 10.3, 13.2, 14.7, 17.6, etc...]
        Slotted services have capacities [1, 3, 1, 3, 1, 3, 1, 3 etc....]
        """
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([0.7, 0.7, 1.2, 0.3, 1.4, 1.2, 0.6, 8.9, float('inf')])],
            service_distributions=[ciw.dists.Deterministic(0.2)],
            number_of_servers=[ciw.Slotted(slots=[1.5, 4.4], slot_sizes=[1, 3])]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20)
        recs = Q.get_all_records()
        recs = sorted(recs, key=lambda rec: rec.id_number)

        self.assertEqual(len(Q.nodes[-1].all_individuals), 8)

        expected_service_dates = [1.5, 4.4, 4.4, 4.4, 5.9, 8.8, 8.8, 17.6]
        observed_service_dates = [r.service_start_date for r in recs]
        self.assertEqual(observed_service_dates, expected_service_dates)

    def test_noncapacitated_slotted_services_with_overruns(self):
        """
        Arrivals occur at times [0.3, 0.5, 10.1]
        Service times are [2.5, 4.5, 0.5]
        Services are slotted at times [1, 3, 5, 11]
        Slotted services have capacities [2, 1, 1, 1]
        """
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([0.3, 0.2, 9.6, float('inf')])],
            service_distributions=[ciw.dists.Sequential([2.5, 4.5, 0.5, 1000])],
            number_of_servers=[ciw.Slotted(slots=[1, 3, 5, 11], slot_sizes=[2, 1, 1, 1])]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(20)
        recs = Q.get_all_records()
        recs = sorted(recs, key=lambda rec: rec.id_number)

        self.assertEqual(len(Q.nodes[-1].all_individuals), 3)

        expected_service_dates = [1, 1, 11]
        observed_service_dates = [r.service_start_date for r in recs]
        self.assertEqual(observed_service_dates, expected_service_dates)

    def test_slotted_services_capacitated(self):
        """
        Tests when the service times of slotted services last longer
        than the gap between the slots.
        Two options
          - capacitated=False : allows `slot_size` to be served, even if previous customers are still in service
          - capacitated=True  : only allows `slot_size` customers to be served, at a time, so if previous customers are still in service, less than `slot_size` new customers will be served.

        Example:
          - Arrival times = [0.5, 1.1, 1.5, 1.7, 2.5]
          - Service times = [0.2, 0.2, 1.2, 0.2, 0.5]
          - Slot times = [2, 3, 5, 6, ...]
          - Slot sizes = [4, 1, 4, 1, ...]
        """
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([0.5, 0.6, 0.4, 0.3, 0.8, float('inf')])],
            service_distributions=[ciw.dists.Sequential([0.2, 0.2, 1.2, 0.2, 0.5])],
            number_of_servers=[ciw.Slotted(slots=[2, 3], slot_sizes=[4, 1], capacitated=False)]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(10)
        recs = Q.get_all_records()
        recs = sorted(recs, key=lambda rec: rec.id_number)
        self.assertEqual(len(Q.nodes[-1].all_individuals), 5)
        expected_service_dates = [2, 2, 2, 2, 3]
        observed_service_dates = [r.service_start_date for r in recs]
        self.assertEqual(observed_service_dates, expected_service_dates)

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([0.5, 0.6, 0.4, 0.3, 0.8, float('inf')])],
            service_distributions=[ciw.dists.Sequential([0.2, 0.2, 1.2, 0.2, 0.5])],
            number_of_servers=[ciw.Slotted(slots=[2, 3], slot_sizes=[4, 1], capacitated=True)]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(10)
        recs = Q.get_all_records()
        recs = sorted(recs, key=lambda rec: rec.id_number)
        self.assertEqual(len(Q.nodes[-1].all_individuals), 5)
        expected_service_dates = [2, 2, 2, 2, 5]
        observed_service_dates = [r.service_start_date for r in recs]
        self.assertEqual(observed_service_dates, expected_service_dates)

    def test_invalid_preemption_options(self):
        self.assertRaises(ValueError, lambda: ciw.Schedule(numbers_of_servers=[2, 1], shift_end_dates=[10, 12], preemption='something'))
        self.assertRaises(ValueError, lambda: ciw.Slotted(slots=[2, 3], slot_sizes=[4, 1], capacitated=False, preemption='resume'))
        self.assertRaises(ValueError, lambda: ciw.Slotted(slots=[2, 3], slot_sizes=[4, 1], capacitated=True, preemption='something'))

    def test_slotted_services_capacitated_preemption(self):
        """
        Tests when the service times of slotted services last longer
        than the gap between the slots, and jobs are pre-empted

        Example:
          - Arrival times = [0.3, 0.5]
          - Service times = [10, 10]
          - Slot times = [4, 11, 15, 27, ...]
          - Slot sizes = [3, 1, 3, 1, ...]
        """
        # No preemption
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([0.3, 0.2, float('inf')])],
            service_distributions=[ciw.dists.Sequential([10, 10, 1])],
            number_of_servers=[ciw.Slotted(slots=[4, 11], slot_sizes=[3, 1], capacitated=True)]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(50)
        recs = Q.get_all_records()
        recs = sorted(recs, key=lambda rec: rec.id_number)
        self.assertEqual(len(Q.nodes[-1].all_individuals), 2)

        self.assertEqual(recs[0].id_number, 1)
        self.assertEqual(recs[0].arrival_date, 0.3)
        self.assertEqual(recs[0].service_start_date, 4)
        self.assertEqual(recs[0].service_end_date, 14)
        self.assertEqual(recs[0].exit_date, 14)
        self.assertEqual(recs[0].record_type, 'service')

        self.assertEqual(recs[1].id_number, 2)
        self.assertEqual(recs[1].arrival_date, 0.5)
        self.assertEqual(recs[1].service_start_date, 4)
        self.assertEqual(recs[1].service_end_date, 14)
        self.assertEqual(recs[1].exit_date, 14)
        self.assertEqual(recs[1].record_type, 'service')

        # preemption='resume'
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([0.3, 0.2, float('inf')])],
            service_distributions=[ciw.dists.Sequential([10, 10, 1])],
            number_of_servers=[ciw.Slotted(slots=[4, 11], slot_sizes=[3, 1], capacitated=True, preemption='resume')]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(50)
        recs = Q.get_all_records()
        recs = sorted(recs, key=lambda rec: rec.id_number)
        self.assertEqual(len(Q.nodes[-1].all_individuals), 2)

        self.assertEqual(recs[0].id_number, 1)
        self.assertEqual(recs[0].arrival_date, 0.3)
        self.assertEqual(recs[0].service_start_date, 4)
        self.assertEqual(recs[0].service_end_date, 14)
        self.assertEqual(recs[0].exit_date, 14)
        self.assertEqual(recs[0].record_type, 'service')

        self.assertEqual(recs[1].id_number, 2)
        self.assertEqual(recs[1].arrival_date, 0.5)
        self.assertEqual(recs[1].service_start_date, 4)
        self.assertEqual(recs[1].service_time, 10)
        self.assertTrue(math.isnan(recs[1].service_end_date))
        self.assertEqual(recs[1].exit_date, 11)
        self.assertEqual(recs[1].record_type, 'interrupted service')

        self.assertEqual(recs[2].id_number, 2)
        self.assertEqual(recs[2].arrival_date, 0.5)
        self.assertEqual(recs[2].service_start_date, 15)
        self.assertEqual(recs[2].service_time, 3)
        self.assertEqual(recs[2].service_end_date, 18)
        self.assertEqual(recs[2].exit_date, 18)
        self.assertEqual(recs[2].record_type, 'service')

        # preemption='resample'
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([0.3, 0.2, float('inf')])],
            service_distributions=[ciw.dists.Sequential([10, 10, 1])],
            number_of_servers=[ciw.Slotted(slots=[4, 11], slot_sizes=[3, 1], capacitated=True, preemption='resample')]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(50)
        recs = Q.get_all_records()
        recs = sorted(recs, key=lambda rec: rec.id_number)
        self.assertEqual(len(Q.nodes[-1].all_individuals), 2)

        self.assertEqual(recs[0].id_number, 1)
        self.assertEqual(recs[0].arrival_date, 0.3)
        self.assertEqual(recs[0].service_start_date, 4)
        self.assertEqual(recs[0].service_end_date, 14)
        self.assertEqual(recs[0].exit_date, 14)
        self.assertEqual(recs[0].record_type, 'service')

        self.assertEqual(recs[1].id_number, 2)
        self.assertEqual(recs[1].arrival_date, 0.5)
        self.assertEqual(recs[1].service_start_date, 4)
        self.assertEqual(recs[1].service_time, 10)
        self.assertTrue(math.isnan(recs[1].service_end_date))
        self.assertEqual(recs[1].exit_date, 11)
        self.assertEqual(recs[1].record_type, 'interrupted service')

        self.assertEqual(recs[2].id_number, 2)
        self.assertEqual(recs[2].arrival_date, 0.5)
        self.assertEqual(recs[2].service_start_date, 15)
        self.assertEqual(recs[2].service_time, 1)
        self.assertEqual(recs[2].service_end_date, 16)
        self.assertEqual(recs[2].exit_date, 16)
        self.assertEqual(recs[2].record_type, 'service')

        # preemption='restart'
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([0.3, 0.2, float('inf')])],
            service_distributions=[ciw.dists.Sequential([10, 10, 1])],
            number_of_servers=[ciw.Slotted(slots=[4, 11], slot_sizes=[3, 1], capacitated=True, preemption='restart')]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(50)
        recs = Q.get_all_records()
        recs = sorted(recs, key=lambda rec: rec.id_number)
        self.assertEqual(len(Q.nodes[-1].all_individuals), 2)

        self.assertEqual(recs[0].id_number, 1)
        self.assertEqual(recs[0].arrival_date, 0.3)
        self.assertEqual(recs[0].service_start_date, 4)
        self.assertEqual(recs[0].service_end_date, 14)
        self.assertEqual(recs[0].exit_date, 14)
        self.assertEqual(recs[0].record_type, 'service')

        self.assertEqual(recs[1].id_number, 2)
        self.assertEqual(recs[1].arrival_date, 0.5)
        self.assertEqual(recs[1].service_start_date, 4)
        self.assertEqual(recs[1].service_time, 10)
        self.assertTrue(math.isnan(recs[1].service_end_date))
        self.assertEqual(recs[1].exit_date, 11)
        self.assertEqual(recs[1].record_type, 'interrupted service')

        self.assertEqual(recs[2].id_number, 2)
        self.assertEqual(recs[2].arrival_date, 0.5)
        self.assertEqual(recs[2].service_start_date, 15)
        self.assertEqual(recs[2].service_time, 10)
        self.assertEqual(recs[2].service_end_date, 25)
        self.assertEqual(recs[2].exit_date, 25)
        self.assertEqual(recs[2].record_type, 'service')

    def test_offset_error_raising(self):
        self.assertRaises(ValueError, lambda: ciw.Slotted(slots=[4, 11], slot_sizes=[3, 1], offset='something'))
        self.assertRaises(ValueError, lambda: ciw.Slotted(slots=[4, 11], slot_sizes=[3, 1], offset=-6.7))
        self.assertRaises(ValueError, lambda: ciw.Schedule(numbers_of_servers=[1, 2], shift_end_dates=[10, 25], offset='something'))
        self.assertRaises(ValueError, lambda: ciw.Schedule(numbers_of_servers=[1, 2], shift_end_dates=[10, 25], offset=-6.7))

    def test_schedules_with_offset(self):
        """
        First with no offset
        """
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([0.1, float('inf')])],
            service_distributions=[ciw.dists.Deterministic(10)],
            batching_distributions=[ciw.dists.Deterministic(10)],
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 0, 6, 0], shift_end_dates=[5, 20, 23, 30])]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(3000)
        recs = Q.get_all_records()

        expected_service_dates = [0.1, 20, 20, 20, 20, 20, 20, 30, 50, 50]
        self.assertEqual(expected_service_dates, [r.service_start_date for r in recs])
        """
        Now with an offset
        """
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([0.1, float('inf')])],
            service_distributions=[ciw.dists.Deterministic(10)],
            batching_distributions=[ciw.dists.Deterministic(10)],
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 0, 6, 0], shift_end_dates=[5, 20, 23, 30], offset=0.5)]
        )
        Q = ciw.Simulation(N)
        Q.simulate_until_max_time(3000)
        recs = Q.get_all_records()

        expected_service_dates = [0.5, 20.5, 20.5, 20.5, 20.5, 20.5, 20.5, 30.5, 50.5, 50.5]
        self.assertEqual(expected_service_dates, [r.service_start_date for r in recs])

