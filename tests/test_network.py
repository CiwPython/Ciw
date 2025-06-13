import unittest
import ciw
import copy
import random
from hypothesis import given
from hypothesis.strategies import floats, integers, lists, random_module


def example_baulking_function(n):
    if n < 5:
        return 0.0
    return 1.0


class TestServiceCentre(unittest.TestCase):
    def test_init_method(self):
        number_of_servers = 2
        queueing_capacity = float("inf")
        class_change_matrix = {'Class 0': {'Class 0': 0.2, 'Class 1': 0.8}, 'Class 1': {'Class 0': 1.0, 'Class 1': 0.0}}
        SC = ciw.ServiceCentre(
            number_of_servers,
            queueing_capacity,
            class_change_matrix
        )
        self.assertEqual(SC.number_of_servers, number_of_servers)
        self.assertEqual(SC.queueing_capacity, queueing_capacity)
        self.assertEqual(SC.class_change_matrix, class_change_matrix)

    @given(
        number_of_servers=integers(min_value=1),
        queueing_capacity=integers(min_value=0),
        class_change_prob1=floats(min_value=0.0, max_value=1.0),
        class_change_prob2=floats(min_value=0.0, max_value=1.0),
    )
    def test_init_method_h(
        self,
        number_of_servers,
        queueing_capacity,
        class_change_prob1,
        class_change_prob2,
    ):
        class_change_matrix = {
            'Class 0': {'Class 0': class_change_prob1, 'Class 1': 1 - class_change_prob1},
            'Class 1': {'Class 0': class_change_prob2, 'Class 1': 1 - class_change_prob2}
        }
        SC = ciw.ServiceCentre(
            number_of_servers,
            queueing_capacity,
            class_change_matrix
        )
        self.assertEqual(SC.number_of_servers, number_of_servers)
        self.assertEqual(SC.queueing_capacity, queueing_capacity)
        self.assertEqual(SC.class_change_matrix, class_change_matrix)


class TestCustomerClass(unittest.TestCase):
    def test_init_method(self):
        arrival_distributions = [
            ciw.dists.Uniform(4.0, 9.0),
            ciw.dists.Exponential(5),
            ciw.dists.Gamma(0.6, 1.2),
        ]
        service_distributions = [
            ciw.dists.Gamma(4.0, 9.0),
            ciw.dists.Uniform(0.6, 1.2),
            ciw.dists.Exponential(5),
        ]
        routing = [[0.2, 0.6, 0.2], [0, 0, 0], [0.5, 0, 0]]
        priority_class = 2
        baulking_functions = [None, None, example_baulking_function]
        batching_distributions = [
            ciw.dists.Deterministic(1),
            ciw.dists.Deterministic(1),
            ciw.dists.Deterministic(1),
        ]
        reneging_time_distributions = [None, None, None]
        class_change_time_distributions = [None]

        CC = ciw.CustomerClass(
            arrival_distributions,
            service_distributions,
            routing,
            priority_class,
            baulking_functions,
            batching_distributions,
            reneging_time_distributions,
            class_change_time_distributions,
        )
        self.assertEqual(CC.arrival_distributions, arrival_distributions)
        self.assertEqual(CC.service_distributions, service_distributions)
        self.assertEqual(CC.batching_distributions, batching_distributions)
        self.assertEqual(CC.routing, routing)
        self.assertEqual(CC.priority_class, priority_class)
        self.assertEqual(CC.reneging_time_distributions, reneging_time_distributions)
        self.assertEqual(CC.class_change_time_distributions, class_change_time_distributions)

        # check baulking function works
        self.assertEqual(CC.baulking_functions[2](0), 0.0)
        self.assertEqual(CC.baulking_functions[2](1), 0.0)
        self.assertEqual(CC.baulking_functions[2](2), 0.0)
        self.assertEqual(CC.baulking_functions[2](3), 0.0)
        self.assertEqual(CC.baulking_functions[2](4), 0.0)
        self.assertEqual(CC.baulking_functions[2](5), 1.0)
        self.assertEqual(CC.baulking_functions[2](6), 1.0)
        self.assertEqual(CC.baulking_functions[2](7), 1.0)
        self.assertEqual(CC.baulking_functions[2](8), 1.0)


class TestNetwork(unittest.TestCase):
    def test_init_method(self):
        number_of_servers = 2
        queueing_capacity = float("inf")
        class_change_matrix = {'Class 0': {'Class 0': 0.2, 'Class 1': 0.8}, 'Class 1': {'Class 0': 1.0, 'Class 1': 0.0}}
        arrival_distributions = [
            ciw.dists.Uniform(4.0, 9.0),
            ciw.dists.Exponential(5.0),
            ciw.dists.Gamma(0.6, 1.2),
        ]
        service_distributions = [
            ciw.dists.Gamma(4.0, 9.0),
            ciw.dists.Uniform(0.6, 1.2),
            ciw.dists.Exponential(5),
        ]
        routing = [[0.2, 0.6, 0.2], [0.0, 0.0, 0.0], [0.5, 0.0, 0.0]]
        priority_class = 0
        batching_distributions = [
            ciw.dists.Deterministic(1),
            ciw.dists.Deterministic(1),
            ciw.dists.Deterministic(1),
        ]
        baulking_functions = [None, None, example_baulking_function]
        reneging_time_distributions = [None, None, None]
        class_change_time_distributions = {'Class 0': None, 'Class 1': None}
        service_centres = [
            ciw.ServiceCentre(
                number_of_servers,
                queueing_capacity,
                class_change_matrix
            ) for i in range(3)
        ]
        customer_classes = {f'Class {i}': ciw.CustomerClass(
                arrival_distributions,
                service_distributions,
                routing,
                priority_class,
                baulking_functions,
                batching_distributions,
                reneging_time_distributions,
                class_change_time_distributions,
            ) for i in range(2)
        }
        N = ciw.Network(service_centres, customer_classes)
        self.assertEqual(N.service_centres, service_centres)
        self.assertEqual(N.customer_classes, customer_classes)
        self.assertEqual(N.number_of_nodes, 3)
        self.assertEqual(N.number_of_classes, 2)
        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {'Class 0': 0, 'Class 1': 0})
        self.assertFalse(N.service_centres[0].reneging)
        self.assertFalse(N.service_centres[1].reneging)
        self.assertFalse(N.service_centres[0].class_change_time)
        self.assertFalse(N.service_centres[1].class_change_time)

    def test_create_network_from_dictionary(self):
        params = {
            "arrival_distributions": {"Class 0": [ciw.dists.Exponential(3.0)]},
            "service_distributions": {"Class 0": [ciw.dists.Exponential(7.0)]},
            "number_of_servers": [9],
            "routing": {"Class 0": [[0.5]]},
            "queue_capacities": [float("inf")],
            "ps_thresholds": [4],
        }
        N = ciw.create_network_from_dictionary(params)

        self.assertEqual(N.number_of_nodes, 1)
        self.assertEqual(N.number_of_classes, 1)
        self.assertEqual(N.service_centres[0].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[0].class_change_matrix, None)
        self.assertEqual(N.service_centres[0].ps_threshold, 4)
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].arrival_distributions],
            ["Exponential(rate=3.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].service_distributions],
            ["Exponential(rate=7.0)"],
        )

        router0 = N.customer_classes['Class 0'].routing
        self.assertEqual(router0.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router0.routers[0].probs], [0.5, 0.5])
        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {'Class 0': 0})

        params = {
            "arrival_distributions": [
                ciw.dists.Exponential(3.0),
                ciw.dists.Uniform(0.2, 0.6),
            ],
            "service_distributions": [
                ciw.dists.Exponential(7.0),
                ciw.dists.Deterministic(0.7),
            ],
            "number_of_servers": [ciw.Schedule(numbers_of_servers=[1, 4], shift_end_dates=[20, 50]), 3],
            "routing": [[0.5, 0.2], [0.0, 0.0]],
            "queue_capacities": [10, float("inf")],
        }
        N = ciw.create_network_from_dictionary(params)
        self.assertEqual(N.number_of_nodes, 2)
        self.assertEqual(N.number_of_classes, 1)
        self.assertEqual(N.service_centres[0].queueing_capacity, 10)
        self.assertTrue(type(N.service_centres[0].number_of_servers), ciw.schedules.Schedule)
        self.assertEqual(N.service_centres[0].class_change_matrix, None)
        self.assertEqual(N.service_centres[0].number_of_servers.shift_end_dates, [20, 50])
        self.assertEqual(N.service_centres[0].number_of_servers.numbers_of_servers, [1, 4])
        self.assertEqual(N.service_centres[1].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[1].number_of_servers, 3)
        self.assertEqual(N.service_centres[1].class_change_matrix, None)
        self.assertEqual(
            [str(d) for d in N.customer_classes['Customer'].arrival_distributions],
            ["Exponential(rate=3.0)", "Uniform(lower=0.2, upper=0.6)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Customer'].service_distributions],
            ["Exponential(rate=7.0)", "Deterministic(value=0.7)"],
        )
        router = N.customer_classes['Customer'].routing
        self.assertEqual(router.routers[0].destinations, [1, 2, -1])
        self.assertEqual([round(p, 2) for p in router.routers[0].probs], [0.5, 0.2, 0.3])
        self.assertEqual(router.routers[1].destinations, [1, 2, -1])
        self.assertEqual([round(p, 2) for p in router.routers[1].probs], [0.0, 0.0, 1.0])

        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {'Customer': 0})

        params = {
            "arrival_distributions": {
                "Class 0": [ciw.dists.Exponential(3.0)],
                "Class 1": [ciw.dists.Exponential(4.0)],
            },
            "service_distributions": {
                "Class 0": [ciw.dists.Exponential(7.0)],
                "Class 1": [ciw.dists.Uniform(0.4, 1.2)],
            },
            "number_of_servers": [9],
            "routing": {"Class 0": [[0.5]], "Class 1": [[0.0]]},
            "queue_capacities": [float("inf")],
            "class_change_matrices": [{'Class 0': {'Class 0': 0.0, 'Class 1': 1.0}, 'Class 1': {'Class 0': 0.2, 'Class 1': 0.8}}],
        }
        N = ciw.create_network_from_dictionary(params)
        self.assertEqual(N.number_of_nodes, 1)
        self.assertEqual(N.number_of_classes, 2)
        self.assertEqual(N.service_centres[0].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(
            N.service_centres[0].class_change_matrix, {'Class 0': {'Class 0': 0.0, 'Class 1': 1.0}, 'Class 1': {'Class 0': 0.2, 'Class 1': 0.8}}
        )
        self.assertEqual(N.service_centres[0].ps_threshold, 1)
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].arrival_distributions],
            ["Exponential(rate=3.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].service_distributions],
            ["Exponential(rate=7.0)"],
        )
        router0 = N.customer_classes['Class 0'].routing
        router1 = N.customer_classes['Class 1'].routing
        self.assertEqual(router0.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router0.routers[0].probs], [0.5, 0.5])
        self.assertEqual(router1.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router1.routers[0].probs], [0.0, 1.0])
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 1'].arrival_distributions],
            ["Exponential(rate=4.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 1'].service_distributions],
            ["Uniform(lower=0.4, upper=1.2)"],
        )
        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {'Class 0': 0, 'Class 1': 0})

        params = {
            "arrival_distributions": {
                "Class 0": [ciw.dists.Exponential(3.0)],
                "Class 1": [ciw.dists.Exponential(4.0)],
            },
            "service_distributions": {
                "Class 0": [ciw.dists.Exponential(7.0)],
                "Class 1": [ciw.dists.Uniform(0.4, 1.2)],
            },
            "number_of_servers": [9],
            "routing": {"Class 0": [[0.5]], "Class 1": [[0.0]]},
            "class_change_time_distributions": {
                'Class 0': {'Class 0': None, 'Class 1': ciw.dists.Deterministic(5)},
                'Class 1': {'Class 0': ciw.dists.Deterministic(10), 'Class 1': None}
            },
        }
        N = ciw.create_network_from_dictionary(params)
        self.assertEqual(N.number_of_nodes, 1)
        self.assertEqual(N.number_of_classes, 2)
        self.assertEqual(N.service_centres[0].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].class_change_time_distributions.values()],
            ["None", "Deterministic(value=5)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 1'].class_change_time_distributions.values()],
            ["Deterministic(value=10)", "None"],
        )
        self.assertEqual(N.service_centres[0].ps_threshold, 1)
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].arrival_distributions],
            ["Exponential(rate=3.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].service_distributions],
            ["Exponential(rate=7.0)"],
        )
        router0 = N.customer_classes['Class 0'].routing
        router1 = N.customer_classes['Class 1'].routing
        self.assertEqual(router0.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router0.routers[0].probs], [0.5, 0.5])
        self.assertEqual(router1.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router1.routers[0].probs], [0.0, 1.0])
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 1'].arrival_distributions],
            ["Exponential(rate=4.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 1'].service_distributions],
            ["Uniform(lower=0.4, upper=1.2)"],
        )
        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {'Class 0': 0, 'Class 1': 0})

        params = {
            "arrival_distributions": {
                "Class 0": [ciw.dists.Exponential(3.0)],
                "Class 1": [ciw.dists.Exponential(4.0)],
            },
            "service_distributions": {
                "Class 0": [ciw.dists.Exponential(7.0)],
                "Class 1": [ciw.dists.Uniform(0.4, 1.2)],
            },
            "number_of_servers": [9],
            "routing": {"Class 0": [[0.5]], "Class 1": [[0.0]]},
            "queue_capacities": [float("inf")],
            "priority_classes": {"Class 0": 1, "Class 1": 0},
        }
        N = ciw.create_network_from_dictionary(params)
        self.assertEqual(N.number_of_nodes, 1)
        self.assertEqual(N.number_of_classes, 2)
        self.assertEqual(N.service_centres[0].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[0].ps_threshold, 1)
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].arrival_distributions],
            ["Exponential(rate=3.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].service_distributions],
            ["Exponential(rate=7.0)"],
        )
        router0 = N.customer_classes['Class 0'].routing
        router1 = N.customer_classes['Class 1'].routing
        self.assertEqual(router0.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router0.routers[0].probs], [0.5, 0.5])
        self.assertEqual(router1.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router1.routers[0].probs], [0.0, 1.0])
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 1'].arrival_distributions],
            ["Exponential(rate=4.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 1'].service_distributions],
            ["Uniform(lower=0.4, upper=1.2)"],
        )
        self.assertEqual(N.customer_classes['Class 0'].priority_class, 1)
        self.assertEqual(N.customer_classes['Class 1'].priority_class, 0)
        self.assertEqual(N.number_of_priority_classes, 2)
        self.assertEqual(N.priority_class_mapping, {'Class 0': 1, 'Class 1': 0})

        params = {
            "arrival_distributions": [
                ciw.dists.Exponential(3.0),
                ciw.dists.Exponential(4.0),
                ciw.dists.Exponential(2.0),
            ],
            "service_distributions": [
                ciw.dists.Exponential(7.0),
                ciw.dists.Uniform(0.4, 1.2),
                ciw.dists.Deterministic(5.33),
            ],
            "number_of_servers": [9, 2, 4],
            "routing": [[0.5, 0.0, 0.1], [0.2, 0.1, 0.0], [0.0, 0.0, 0.0]],
            "queue_capacities": [float("inf"), float("inf"), float("inf")],
            "baulking_functions": [None, None, example_baulking_function],
        }
        N = ciw.create_network_from_dictionary(params)
        self.assertEqual(N.number_of_nodes, 3)
        self.assertEqual(N.number_of_classes, 1)
        self.assertEqual(N.service_centres[0].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[1].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[1].number_of_servers, 2)
        self.assertEqual(N.service_centres[2].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[2].number_of_servers, 4)

        self.assertEqual(
            [str(d) for d in N.customer_classes['Customer'].arrival_distributions],
            ["Exponential(rate=3.0)", "Exponential(rate=4.0)", "Exponential(rate=2.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Customer'].service_distributions],
            ["Exponential(rate=7.0)", "Uniform(lower=0.4, upper=1.2)", "Deterministic(value=5.33)"],
        )
        router = N.customer_classes['Customer'].routing
        self.assertEqual(router.routers[0].destinations, [1, 2, 3, -1])
        self.assertEqual([round(p, 2) for p in router.routers[0].probs], [0.5, 0.0, 0.1, 0.4])
        self.assertEqual(router.routers[1].destinations, [1, 2, 3, -1])
        self.assertEqual([round(p, 2) for p in router.routers[1].probs], [0.2, 0.1, 0.0, 0.7])
        self.assertEqual(router.routers[2].destinations, [1, 2, 3, -1])
        self.assertEqual([round(p, 2) for p in router.routers[2].probs], [0.0, 0.0, 0.0, 1.0])
        self.assertEqual(
            N.customer_classes['Customer'].baulking_functions,
            [None, None, example_baulking_function],
        )
        self.assertEqual(N.number_of_priority_classes, 1)


    def test_raising_errors(self):
        params = {
            "arrival_distributions": {"Class 0": [ciw.dists.Exponential(3.0)]},
            "service_distributions": {"Class 0": [ciw.dists.Exponential(7.0)]},
            "number_of_servers": [9],
            "number_of_classes": 1,
            "routing": {"Class 0": [[0.5]]},
            "number_of_nodes": 1,
            "queue_capacities": [float("inf")],
        }
        params_list = [copy.deepcopy(params) for i in range(24)]

        params_list[0]["number_of_classes"] = -2
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[0]
        )
        params_list[1]["number_of_nodes"] = -2
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[1]
        )
        params_list[2]["number_of_servers"] = [5, 6, 7]
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[2]
        )
        params_list[3]["number_of_servers"] = [-3]
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[3]
        )
        params_list[4]["number_of_servers"] = ["my_missing_schedule"]
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[4]
        )
        params_list[5]["queue_capacities"] = [float("Inf"), 1, 2]
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[5]
        )
        params_list[6]["queue_capacities"] = [-2]
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[6]
        )
        params_list[7]["arrival_distributions"] = {
            "Class 0": [ciw.dists.Exponential(3.2)],
            "Class 1": [ciw.dists.Exponential(2.1)],
        }
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[7]
        )
        params_list[8]["arrival_distributions"] = {"Patient 0": [ciw.dists.Exponential(11.5)]}
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[8]
        )
        params_list[9]["arrival_distributions"]["Class 0"] = [
            ciw.dists.Exponential(3.1),
            ciw.dists.Exponential(2.4)
        ]
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[9]
        )
        params_list[10]["service_distributions"] = {
            "Class 0": [ciw.dists.Exponential(3.2)],
            "Class 1": [ciw.dists.Exponential(2.1)],
        }
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[10]
        )
        params_list[11]["service_distributions"] = {
            "Patient 0": [ciw.dists.Exponential(11.5)]
        }
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[11]
        )
        params_list[12]["service_distributions"]["Class 0"] = [
            ciw.dists.Exponential(3.1),
            ciw.dists.Exponential(2.4)
        ]
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[12]
        )
        params_list[13]["routing"] = {"Class 0": [[0.2]], "Class 1": [[0.3]]}
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[13]
        )
        params_list[14]["routing"] = {"Patient 0": [[0.5]]}
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[14]
        )
        params_list[15]["routing"]["Class 0"] = [[0.2], [0.1]]
        N = ciw.create_network_from_dictionary(params_list[15])
        self.assertRaises(
            ValueError,
            ciw.Simulation,
            N
        )
        params_list[16]["routing"]["Class 0"] = [[0.2, 0.1]]
        N = ciw.create_network_from_dictionary(params_list[16])
        self.assertRaises(
            ValueError,
            ciw.Simulation,
            N
        )
        params_list[17]["routing"]["Class 0"] = [[-0.6]]
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[17]
        )
        params_list[18]["routing"]["Class 0"] = [[1.4]]
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[18]
        )
        params_list[19]["class_change_matrices"] = [
            {'Class 0': {'Class 0': 0.0, 'Class 1': 0.0}},
            {'Class 0': {'Class 0': 0.0, 'Class 1': 0.0}},
        ]
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[19]
        )
        params_list[20]["class_change_matrices"] = {"Class 0": 0.0}
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[20]
        )
        params_list[20]["class_change_matrices"] = [{"Class 7": {'Class 0': 0.0}}]
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[20]
        )

        params_list[21]["reneging_time_distributions"] = {
            "Class 0": [ciw.dists.Exponential(1), ciw.dists.Exponential(1)]
        }
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[21]
        )
        params_list[22]["class_change_time_distributions"] = {'Class 0': {'Class 0': None}, 'Class 1': {'Class 0': None, 'Class 1': None}}
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[22]
        )
        params_list[23]["routing"]["Class 0"] = [['0.5']]
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params_list[23]
        )

    def test_raising_errors_routing(self):
        params = {
            'arrival_distributions': [ciw.dists.Exponential(1.0), ciw.dists.Exponential(1.0)],
            'service_distributions': [ciw.dists.Exponential(2.0), ciw.dists.Exponential(2.0)],
            'number_of_servers': [2, 1],
            'routing': [[0.5, 0.6], [0.0, 0.3]]
        }
        self.assertRaises(
            ValueError,
            ciw.create_network_from_dictionary,
            params
        )

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(1.0), ciw.dists.Exponential(1.0)],
            service_distributions=[ciw.dists.Exponential(2.0), ciw.dists.Exponential(2.0)],
            number_of_servers=[2, 1],
            routing=[[0.5, 0.2, 0.0], [0.0, 0.3, 0.0], [0.1, 0.1, 0.3]]
        )
        self.assertRaises(
            ValueError,
            ciw.Simulation,
            N
        )

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(1.0), ciw.dists.Exponential(1.0)],
            service_distributions=[ciw.dists.Exponential(2.0), ciw.dists.Exponential(2.0)],
            number_of_servers=[2, 1],
            routing=ciw.routing.NetworkRouting(routers=[
                ciw.routing.Probabilistic(destinations=[0, 1], probs=[0.5, 0.2]),
                ciw.routing.Probabilistic(destinations=[0, 2], probs=[0.5, 0.2])
            ])
        )
        self.assertRaises(
            ValueError,
            ciw.Simulation,
            N
        )


class TestImportNoMatrix(unittest.TestCase):
    def test_optional_transition_matrix(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(1.0)],
            service_distributions=[ciw.dists.Exponential(2.0)],
            number_of_servers=[1],
        )
        router = N.customer_classes['Customer'].routing
        self.assertEqual(router.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router.routers[0].probs], [0.0, 1.0])

        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Exponential(1.0)],
                "Class 1": [ciw.dists.Exponential(1.0)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Exponential(2.0)],
                "Class 1": [ciw.dists.Exponential(1.0)],
            },
            number_of_servers=[1],
        )

        router0 = N.customer_classes['Class 0'].routing
        router1 = N.customer_classes['Class 1'].routing
        self.assertEqual(router0.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router0.routers[0].probs], [0.0, 1.0])
        self.assertEqual(router1.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router1.routers[0].probs], [0.0, 1.0])

        params = {
            "arrival_distributions": [
                ciw.dists.Exponential(1.0),
                ciw.dists.Exponential(1.0),
            ],
            "service_distributions": [
                ciw.dists.Exponential(2.0),
                ciw.dists.Exponential(2.0),
            ],
            "number_of_servers": [1, 2],
        }
        N = ciw.create_network(**params)
        self.assertRaises(
            ValueError,
            ciw.Simulation,
            N
        )


class TestCreateNetworkKwargs(unittest.TestCase):
    def test_network_from_kwargs(self):
        N = ciw.create_network(
            arrival_distributions={"Class 0": [ciw.dists.Exponential(3.0)]},
            service_distributions={"Class 0": [ciw.dists.Exponential(7.0)]},
            number_of_servers=[9],
            routing={"Class 0": [[0.5]]},
            queue_capacities=[float("inf")],
        )

        self.assertEqual(N.number_of_nodes, 1)
        self.assertEqual(N.number_of_classes, 1)
        self.assertEqual(N.service_centres[0].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[0].class_change_matrix, None)
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].arrival_distributions],
            ["Exponential(rate=3.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].service_distributions],
            ["Exponential(rate=7.0)"],
        )
        router0 = N.customer_classes['Class 0'].routing
        self.assertEqual(router0.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router0.routers[0].probs], [0.5, 0.5])
        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {'Class 0': 0})

        N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Exponential(3.0),
                ciw.dists.Uniform(0.2, 0.6),
            ],
            service_distributions=[
                ciw.dists.Exponential(7.0),
                ciw.dists.Deterministic(0.7),
            ],
            number_of_servers=[ciw.Schedule(numbers_of_servers=[1, 4], shift_end_dates=[20, 50]), 3],
            routing=[[0.5, 0.2], [0.0, 0.0]],
            queue_capacities=[10, float("inf")],
        )

        self.assertEqual(N.number_of_nodes, 2)
        self.assertEqual(N.number_of_classes, 1)
        self.assertEqual(N.service_centres[0].queueing_capacity, 10)
        self.assertEqual(type(N.service_centres[0].number_of_servers), ciw.schedules.Schedule)
        self.assertEqual(N.service_centres[0].class_change_matrix, None)
        self.assertEqual(N.service_centres[0].number_of_servers.shift_end_dates, [20, 50])
        self.assertEqual(N.service_centres[0].number_of_servers.numbers_of_servers, [1, 4])
        self.assertFalse(N.service_centres[0].number_of_servers.preemption)
        self.assertEqual(N.service_centres[1].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[1].number_of_servers, 3)
        self.assertEqual(N.service_centres[1].class_change_matrix, None)
        self.assertEqual(
            [str(d) for d in N.customer_classes['Customer'].arrival_distributions],
            ["Exponential(rate=3.0)", "Uniform(lower=0.2, upper=0.6)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Customer'].service_distributions],
            ["Exponential(rate=7.0)", "Deterministic(value=0.7)"],
        )
        router = N.customer_classes['Customer'].routing
        self.assertEqual(router.routers[0].destinations, [1, 2, -1])
        self.assertEqual([round(p, 2) for p in router.routers[0].probs], [0.5, 0.2, 0.3])
        self.assertEqual(router.routers[1].destinations, [1, 2, -1])
        self.assertEqual([round(p, 2) for p in router.routers[1].probs], [0.0, 0.0, 1.0])

        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {'Customer': 0})

        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Exponential(3.0)],
                "Class 1": [ciw.dists.Exponential(4.0)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Exponential(7.0)],
                "Class 1": [ciw.dists.Uniform(0.4, 1.2)],
            },
            number_of_servers=[9],
            routing={"Class 0": [[0.5]], "Class 1": [[0.0]]},
            queue_capacities=[float("inf")],
            class_change_matrices=[{'Class 0': {'Class 0': 0.0, 'Class 1': 1.0}, 'Class 1': {'Class 0': 0.2, 'Class 1': 0.8}}],
        )

        self.assertEqual(N.number_of_nodes, 1)
        self.assertEqual(N.number_of_classes, 2)
        self.assertEqual(N.service_centres[0].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(
            N.service_centres[0].class_change_matrix, {'Class 0': {'Class 0': 0.0, 'Class 1': 1.0}, 'Class 1': {'Class 0': 0.2, 'Class 1': 0.8}}
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].arrival_distributions],
            ["Exponential(rate=3.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].service_distributions],
            ["Exponential(rate=7.0)"],
        )
        router0 = N.customer_classes['Class 0'].routing
        router1 = N.customer_classes['Class 1'].routing
        self.assertEqual(router0.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router0.routers[0].probs], [0.5, 0.5])
        self.assertEqual(router1.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router1.routers[0].probs], [0.0, 1.0])
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 1'].arrival_distributions],
            ["Exponential(rate=4.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 1'].service_distributions],
            ["Uniform(lower=0.4, upper=1.2)"],
        )
        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {'Class 0': 0, 'Class 1': 0})

        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Exponential(3.0)],
                "Class 1": [ciw.dists.Exponential(4.0)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Exponential(7.0)],
                "Class 1": [ciw.dists.Uniform(0.4, 1.2)],
            },
            number_of_servers=[9],
            routing={"Class 0": [[0.5]], "Class 1": [[0.0]]},
            queue_capacities=[float("Inf")],
            priority_classes={"Class 0": 1, "Class 1": 0},
        )

        self.assertEqual(N.number_of_nodes, 1)
        self.assertEqual(N.number_of_classes, 2)
        self.assertEqual(N.service_centres[0].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].arrival_distributions],
            ["Exponential(rate=3.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].service_distributions],
            ["Exponential(rate=7.0)"],
        )
        router0 = N.customer_classes['Class 0'].routing
        router1 = N.customer_classes['Class 1'].routing
        self.assertEqual(router0.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router0.routers[0].probs], [0.5, 0.5])
        self.assertEqual(router1.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router1.routers[0].probs], [0.0, 1.0])
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 1'].arrival_distributions],
            ["Exponential(rate=4.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 1'].service_distributions],
            ["Uniform(lower=0.4, upper=1.2)"],
        )
        self.assertEqual(N.customer_classes['Class 0'].priority_class, 1)
        self.assertEqual(N.customer_classes['Class 1'].priority_class, 0)
        self.assertEqual(N.number_of_priority_classes, 2)
        self.assertEqual(N.priority_class_mapping, {'Class 0': 1, 'Class 1': 0})

        N = ciw.create_network(
            arrival_distributions=[
                ciw.dists.Exponential(3.0),
                ciw.dists.Exponential(4.0),
                ciw.dists.Exponential(2.0),
            ],
            service_distributions=[
                ciw.dists.Exponential(7.0),
                ciw.dists.Uniform(0.4, 1.2),
                ciw.dists.Deterministic(5.33),
            ],
            number_of_servers=[9, 2, 4],
            routing=[[0.5, 0.0, 0.1], [0.2, 0.1, 0.0], [0.0, 0.0, 0.0]],
            queue_capacities=[float("inf"), float("inf"), float("inf")],
            baulking_functions=[None, None, example_baulking_function],
        )

        self.assertEqual(N.number_of_nodes, 3)
        self.assertEqual(N.number_of_classes, 1)
        self.assertEqual(N.service_centres[0].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(N.service_centres[1].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[1].number_of_servers, 2)
        self.assertEqual(N.service_centres[2].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[2].number_of_servers, 4)

        self.assertEqual(
            [str(d) for d in N.customer_classes['Customer'].arrival_distributions],
            ["Exponential(rate=3.0)", "Exponential(rate=4.0)", "Exponential(rate=2.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Customer'].service_distributions],
            ["Exponential(rate=7.0)", "Uniform(lower=0.4, upper=1.2)", "Deterministic(value=5.33)"],
        )
        router = N.customer_classes['Customer'].routing
        self.assertEqual(router.routers[0].destinations, [1, 2, 3, -1])
        self.assertEqual([round(p, 2) for p in router.routers[0].probs], [0.5, 0.0, 0.1, 0.4])
        self.assertEqual(router.routers[1].destinations, [1, 2, 3, -1])
        self.assertEqual([round(p, 2) for p in router.routers[1].probs], [0.2, 0.1, 0.0, 0.7])
        self.assertEqual(router.routers[2].destinations, [1, 2, 3, -1])
        self.assertEqual([round(p, 2) for p in router.routers[2].probs], [0.0, 0.0, 0.0, 1.0])

        self.assertEqual(
            N.customer_classes['Customer'].baulking_functions,
            [None, None, example_baulking_function],
        )
        self.assertEqual(N.number_of_priority_classes, 1)

        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(5), ciw.dists.Exponential(5)],
            service_distributions=[ciw.dists.Exponential(4), ciw.dists.Exponential(3)],
            number_of_servers=[2, 2],
            routing=[[0.0, 1.0], [0.2, 0.2]],
            reneging_time_distributions=[ciw.dists.Exponential(1), None],
        )
        self.assertEqual(N.number_of_nodes, 2)
        self.assertEqual(N.number_of_classes, 1)
        self.assertEqual(N.service_centres[0].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[0].number_of_servers, 2)
        self.assertTrue(N.service_centres[0].reneging)
        self.assertEqual(N.service_centres[1].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[1].number_of_servers, 2)
        self.assertFalse(N.service_centres[1].reneging)
        self.assertEqual(
            str(N.customer_classes['Customer'].reneging_time_distributions[0]), "Exponential(rate=1)"
        )
        self.assertEqual(N.customer_classes['Customer'].reneging_time_distributions[1], None)

        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Exponential(3.0)],
                "Class 1": [ciw.dists.Exponential(4.0)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Exponential(7.0)],
                "Class 1": [ciw.dists.Uniform(0.4, 1.2)],
            },
            number_of_servers=[9],
            routing={"Class 0": [[0.5]], "Class 1": [[0.0]]},
            class_change_time_distributions={
                'Class 0': {'Class 0': None, 'Class 1': ciw.dists.Deterministic(5)},
                'Class 1': {'Class 0': ciw.dists.Deterministic(10), 'Class 1': None}
            },
        )
        self.assertEqual(N.number_of_nodes, 1)
        self.assertEqual(N.number_of_classes, 2)
        self.assertEqual(N.service_centres[0].queueing_capacity, float("inf"))
        self.assertEqual(N.service_centres[0].number_of_servers, 9)
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].class_change_time_distributions.values()],
            ["None", "Deterministic(value=5)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 1'].class_change_time_distributions.values()],
            ["Deterministic(value=10)", "None"],
        )
        self.assertEqual(N.service_centres[0].ps_threshold, 1)
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].arrival_distributions],
            ["Exponential(rate=3.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 0'].service_distributions],
            ["Exponential(rate=7.0)"],
        )
        router0 = N.customer_classes['Class 0'].routing
        router1 = N.customer_classes['Class 1'].routing
        self.assertEqual(router0.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router0.routers[0].probs], [0.5, 0.5])
        self.assertEqual(router1.routers[0].destinations, [1, -1])
        self.assertEqual([round(p, 2) for p in router1.routers[0].probs], [0.0, 1.0])

        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 1'].arrival_distributions],
            ["Exponential(rate=4.0)"],
        )
        self.assertEqual(
            [str(d) for d in N.customer_classes['Class 1'].service_distributions],
            ["Uniform(lower=0.4, upper=1.2)"],
        )
        self.assertEqual(N.number_of_priority_classes, 1)
        self.assertEqual(N.priority_class_mapping, {'Class 0': 0, 'Class 1': 0})

    def test_create_network_preempt_priorities(self):
        N = ciw.create_network(
            arrival_distributions={
                "Class 0": [ciw.dists.Exponential(3.0), ciw.dists.Exponential(2.0)],
                "Class 1": [ciw.dists.Exponential(4.0), ciw.dists.Exponential(2.0)],
                "Class 2": [ciw.dists.Exponential(3.0), ciw.dists.Exponential(1.0)],
            },
            service_distributions={
                "Class 0": [ciw.dists.Exponential(7.0), ciw.dists.Exponential(5.0)],
                "Class 1": [ciw.dists.Exponential(8.0), ciw.dists.Exponential(1.0)],
                "Class 2": [ciw.dists.Uniform(0.4, 1.2), ciw.dists.Uniform(0.4, 1.2)],
            },
            number_of_servers=[9, 2],
            routing={
                "Class 0": [[0.0, 0.5], [0.1, 0.3]],
                "Class 1": [[0.0, 0.5], [0.3, 0.1]],
                "Class 2": [[0.1, 0.4], [0.3, 0.1]],
            },
            priority_classes=(
                {"Class 0": 0, "Class 1": 1, "Class 2": 0},
                [True, False],
            ),
        )
        self.assertEqual(N.number_of_nodes, 2)
        self.assertEqual(N.number_of_classes, 3)
        self.assertEqual(N.service_centres[0].priority_preempt, True)
        self.assertEqual(N.service_centres[1].priority_preempt, False)
        self.assertEqual(N.customer_classes['Class 0'].priority_class, 0)
        self.assertEqual(N.customer_classes['Class 1'].priority_class, 1)
        self.assertEqual(N.customer_classes['Class 2'].priority_class, 0)

    def test_error_no_arrivals_servers_services(self):
        with self.assertRaises(ValueError):
            ciw.create_network()
        with self.assertRaises(ValueError):
            ciw.create_network(arrival_distributions=[ciw.dists.Exponential(0.2)])
        with self.assertRaises(ValueError):
            ciw.create_network(service_distributions=[ciw.dists.Exponential(0.2)])
        with self.assertRaises(ValueError):
            ciw.create_network(number_of_servers=[1])
        with self.assertRaises(ValueError):
            ciw.create_network(
                arrival_distributions=[ciw.dists.Exponential(0.2)],
                number_of_servers=[1],
            )
        with self.assertRaises(ValueError):
            ciw.create_network(
                arrival_distributions=[ciw.dists.Exponential(0.2)],
                service_distributions=[ciw.dists.Exponential(0.2)],
            )
        with self.assertRaises(ValueError):
            ciw.create_network(
                service_distributions=[ciw.dists.Exponential(0.2)],
                number_of_servers=[1],
            )

    def test_error_extra_args(self):
        params = {
            "arrival_distributions": [ciw.dists.Exponential(3.0)],
            "service_distributions": [ciw.dists.Exponential(7.0)],
            "number_of_servers": [4],
            "something_else": 56,
        }
        with self.assertRaises(TypeError):
            ciw.create_network(**params)

    def test_raise_error_wrong_batch_dist(self):
        params = {
            "arrival_distributions": [ciw.dists.Exponential(3.0)],
            "service_distributions": [ciw.dists.Exponential(7.0)],
            "number_of_servers": [4],
            "batching_distributions": [ciw.dists.Exponential(1.3)],
        }
        N = ciw.create_network(**params)
        with self.assertRaises(ValueError):
            Q = ciw.Simulation(N)
            Q.simulate_until_max_time(10)

    def test_raise_error_invalid_class_change_matrix(self):
        params_geq1 = {
            'arrival_distributions': {
                'Class 0': [ciw.dists.Exponential(5.0)],
                'Class 1': [ciw.dists.Exponential(5.0)]
            },
            'service_distributions': {
                'Class 0': [ciw.dists.Exponential(10.0)],
                'Class 1': [ciw.dists.Exponential(20.0)]
            },
            'number_of_servers': [2],
            'class_change_matrices': [
                {'Class 0': {'Class 0': 0.7, 'Class 1': 0.5},
                 'Class 1': {'Class 0': 1.0, 'Class 1': 0.0}}
            ]
        }
        params_neg = {
            'arrival_distributions': {
                'Class 0': [ciw.dists.Exponential(5.0)],
                'Class 1': [ciw.dists.Exponential(5.0)]
            },
            'service_distributions': {
                'Class 0': [ciw.dists.Exponential(10.0)],
                'Class 1': [ciw.dists.Exponential(20.0)]
            },
            'number_of_servers': [2],
            'class_change_matrices': [
                {'Class 0': {'Class 0': 0.0, 'Class 1': -0.5},
                 'Class 1': {'Class 0': 1.0, 'Class 1': 0.0}}
            ]
        }
        with self.assertRaises(ValueError):
            ciw.create_network(**params_geq1)
        with self.assertRaises(ValueError):
            ciw.create_network(**params_neg)

    def test_raising_errors_system_capacity(self):
        params_neg = {
            'arrival_distributions': [ciw.dists.Exponential(10), ciw.dists.Exponential(10)],
            'service_distributions': [ciw.dists.Exponential(30), ciw.dists.Exponential(20)],
            'number_of_servers': [2, 2],
            'routing': [[0.0, 0.0], [0.0, 0.0]],
            'system_capacity': -4
        }
        params_str = {
            'arrival_distributions': [ciw.dists.Exponential(10), ciw.dists.Exponential(10)],
            'service_distributions': [ciw.dists.Exponential(30), ciw.dists.Exponential(20)],
            'number_of_servers': [2, 2],
            'routing': [[0.0, 0.0], [0.0, 0.0]],
            'system_capacity': '77'
        }
        with self.assertRaises(ValueError):
            ciw.create_network(**params_neg)
        with self.assertRaises(ValueError):
            ciw.create_network(**params_str)
