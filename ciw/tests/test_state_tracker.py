import unittest
import ciw
from decimal import Decimal

class TestStateTracker(unittest.TestCase):
    def test_base_init_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.StateTracker()
        B.initialise(Q)
        self.assertEqual(B.simulation, Q)
        self.assertEqual(B.state, None)

    def test_base_change_state_accept_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.StateTracker()
        B.initialise(Q)
        self.assertEqual(B.state, None)
        B.change_state_accept(1, 1)
        self.assertEqual(B.state, None)

    def test_base_change_state_block_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.StateTracker()
        B.initialise(Q)
        self.assertEqual(B.state, None)
        B.change_state_block(1, 1, 1)
        self.assertEqual(B.state, None)

    def test_base_change_state_release_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.StateTracker()
        B.initialise(Q)
        self.assertEqual(B.state, None)
        B.change_state_release(1, 1, 1, True)
        self.assertEqual(B.state, None)

    def test_base_hash_state_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.StateTracker()
        B.initialise(Q)
        self.assertEqual(B.hash_state(), None)

    def test_base_release_method_within_simulation(self):
        Net = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(Net)
        N = Q.transitive_nodes[2]
        inds = [ciw.Individual(i) for i in range(5)]
        N.individuals = [inds]
        for ind in N.all_individuals:
            srvr = N.find_free_server()
            N.attach_server(srvr, ind)
        self.assertEqual(Q.statetracker.state, None)
        Q.current_time = 43.11
        N.release(0, Q.nodes[1])
        self.assertEqual(Q.statetracker.state, None)
        N.all_individuals[1].is_blocked = True
        Q.current_time = 46.72
        N.release(1, Q.nodes[1])
        self.assertEqual(Q.statetracker.state, None)
        N.release(1, Q.nodes[-1])
        self.assertEqual(Q.statetracker.state, None)

    def test_base_block_method_within_simulation(self):
        Net = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(Net)
        N = Q.transitive_nodes[2]
        self.assertEqual(Q.statetracker.state, None)
        N.block_individual(ciw.Individual(1), Q.nodes[1])
        self.assertEqual(Q.statetracker.state, None)

    def test_base_accept_method_within_simulation(self):
        Net = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(Net)
        N = Q.transitive_nodes[2]
        self.assertEqual(Q.statetracker.state, None)
        Q.current_time = 45.6
        N.accept(ciw.Individual(3, 2))
        self.assertEqual(Q.statetracker.state, None)


class TestSystemPopulation(unittest.TestCase):
    def test_systempop_init_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.SystemPopulation()
        B.initialise(Q)
        self.assertEqual(B.simulation, Q)
        self.assertEqual(B.state, 0)

    def test_systempop_change_state_accept_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.SystemPopulation()
        B.initialise(Q)
        self.assertEqual(B.state, 0)
        B.change_state_accept(1, 1)
        self.assertEqual(B.state, 1)

    def test_systempop_change_state_block_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.SystemPopulation()
        B.initialise(Q)
        B.state = 1
        B.change_state_block(1, 1, 2)
        self.assertEqual(B.state, 1)

    def test_systempop_change_state_release_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.SystemPopulation()
        B.initialise(Q)
        B.state = 15
        B.change_state_release(1, 1, 2, False)
        self.assertEqual(B.state, 14)
        B.change_state_release(1, 1, 2, True)
        self.assertEqual(B.state, 13)

    def test_systempop_hash_state_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.SystemPopulation()
        B.initialise(Q)
        B.state = 13
        self.assertEqual(B.hash_state(), 13)

    def test_systempop_release_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.SystemPopulation())
        N = Q.transitive_nodes[2]
        inds = [ciw.Individual(i) for i in range(5)]
        N.individuals = [inds]
        for ind in N.individuals[0]:
            srvr = N.find_free_server()
            N.attach_server(srvr, ind)
        Q.statetracker.state = 14
        self.assertEqual(Q.statetracker.state, 14)
        Q.current_time = 43.11
        N.release(0, Q.nodes[1])
        self.assertEqual(Q.statetracker.state, 14)
        N.all_individuals[1].is_blocked = True
        Q.current_time = 46.72
        N.release(1, Q.nodes[1])
        self.assertEqual(Q.statetracker.state, 14)
        N.release(1, Q.nodes[-1])
        self.assertEqual(Q.statetracker.state, 13)

    def test_systempop_block_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.SystemPopulation())
        N = Q.transitive_nodes[2]
        Q.statetracker.state = 14
        self.assertEqual(Q.statetracker.state, 14)
        N.block_individual(ciw.Individual(1), Q.nodes[1])
        self.assertEqual(Q.statetracker.state, 14)

    def test_systempop_accept_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.SystemPopulation())
        N = Q.transitive_nodes[2]
        self.assertEqual(Q.statetracker.state, 0)
        Q.current_time = 45.6
        N.accept(ciw.Individual(3, 2))
        self.assertEqual(Q.statetracker.state,  1)


class TestNodePopulation(unittest.TestCase):
    def test_nodepop_init_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NodePopulation()
        B.initialise(Q)
        self.assertEqual(B.simulation, Q)
        self.assertEqual(B.state, [0, 0, 0, 0])

    def test_nodepop_change_state_accept_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NodePopulation()
        B.initialise(Q)
        self.assertEqual(B.state, [0, 0, 0, 0])
        B.change_state_accept(1, 1)
        self.assertEqual(B.state, [1, 0, 0, 0])

    def test_nodepop_change_state_block_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NodePopulation()
        B.initialise(Q)
        B.state = [1, 0, 0, 0]
        B.change_state_block(1, 1, 2)
        self.assertEqual(B.state, [1, 0, 0, 0])

    def test_nodepop_change_state_release_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NodePopulation()
        B.initialise(Q)
        B.state = [3, 3, 1, 8]
        B.change_state_release(1, 1, 2, False)
        self.assertEqual(B.state, [2, 3, 1, 8])
        B.change_state_release(1, 1, 2, True)
        self.assertEqual(B.state, [1, 3, 1, 8])

    def test_nodepop_hash_state_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NodePopulation()
        B.initialise(Q)
        B.state = [7, 3, 1, 0]
        self.assertEqual(B.hash_state(), (7, 3, 1, 0))

    def test_nodepop_release_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.NodePopulation())
        N = Q.transitive_nodes[2]
        inds = [ciw.Individual(i) for i in range(5)]
        N.individuals = [inds]
        for ind in N.individuals[0]:
            srvr = N.find_free_server()
            N.attach_server(srvr, ind)
        Q.statetracker.state = [5, 3, 6, 0]
        self.assertEqual(Q.statetracker.state, [5, 3, 6, 0])
        Q.current_time = 43.11
        N.release(0, Q.nodes[1])
        self.assertEqual(Q.statetracker.state, [6, 3, 5, 0])
        N.all_individuals[1].is_blocked = True
        Q.current_time = 46.72
        N.release(1, Q.nodes[1])
        self.assertEqual(Q.statetracker.state, [7, 3, 4, 0])
        N.release(1, Q.nodes[-1])
        self.assertEqual(Q.statetracker.state, [7, 3, 3, 0])

    def test_nodepop_block_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.NodePopulation())
        N = Q.transitive_nodes[2]
        Q.statetracker.state = [5, 3, 6, 0]
        self.assertEqual(Q.statetracker.state, [5, 3, 6, 0])
        N.block_individual(ciw.Individual(1), Q.nodes[1])
        self.assertEqual(Q.statetracker.state, [5, 3, 6, 0])

    def test_nodepop_accept_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.NodePopulation())
        N = Q.transitive_nodes[2]
        self.assertEqual(Q.statetracker.state, [0, 0, 0, 0])
        Q.current_time = 45.6
        N.accept(ciw.Individual(3, 2))
        self.assertEqual(Q.statetracker.state, [0, 0, 1, 0])


class TestNodeClassMatrix(unittest.TestCase):
    def test_nodeclassmatrix_init_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NodeClassMatrix()
        B.initialise(Q)
        self.assertEqual(B.simulation, Q)
        self.assertEqual(B.state, [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]])

    def test_nodeclassmatrix_change_state_accept_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NodeClassMatrix()
        B.initialise(Q)
        self.assertEqual(B.state, [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]])
        B.change_state_accept(1, 1)
        self.assertEqual(B.state, [[0, 1, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]])

    def test_nodeclassmatrix_change_state_block_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NodeClassMatrix()
        B.initialise(Q)
        B.state = [[0, 1, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
        B.change_state_block(1, 1, 1)
        self.assertEqual(B.state, [[0, 1, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]])

    def test_nodeclassmatrix_change_state_release_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NodeClassMatrix()
        B.initialise(Q)
        B.state = [[0, 1, 2], [1, 1, 1], [0, 1, 0], [4, 3, 1]]
        B.change_state_release(1, 1, 2, False)
        self.assertEqual(B.state, [[0, 1, 1], [1, 1, 1], [0, 1, 0], [4, 3, 1]])
        B.change_state_release(1, 1, 2, True)
        self.assertEqual(B.state, [[0, 1, 0], [1, 1, 1], [0, 1, 0], [4, 3, 1]])

    def test_nodeclassmatrix_hash_state_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NodeClassMatrix()
        B.initialise(Q)
        B.state = [[0, 2, 0], [1, 1, 1], [0, 1, 0], [4, 3, 1]]
        self.assertEqual(B.hash_state(), ((0, 2, 0), (1, 1, 1), (0, 1, 0), (4, 3, 1)))

    def test_nodeclassmatrix_release_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.NodeClassMatrix())
        N = Q.transitive_nodes[2]
        inds = [ciw.Individual(i) for i in range(5)]
        N.individuals = [inds]
        for ind in N.individuals[0]:
            srvr = N.find_free_server()
            N.attach_server(srvr, ind)
        Q.statetracker.state = [[3, 2, 1], [1, 1, 1], [3, 1, 2], [0, 0, 0]]
        self.assertEqual(Q.statetracker.state, [[3, 2, 1], [1, 1, 1], [3, 1, 2], [0, 0, 0]])
        Q.current_time = 43.11
        N.release(0, Q.nodes[1])
        self.assertEqual(Q.statetracker.state, [[4, 2, 1], [1, 1, 1], [2, 1, 2], [0, 0, 0]])
        N.all_individuals[1].is_blocked = True
        Q.current_time = 46.72
        N.release(1, Q.nodes[1])
        self.assertEqual(Q.statetracker.state, [[5, 2, 1], [1, 1, 1], [1, 1, 2], [0, 0, 0]])
        N.release(1, Q.nodes[-1])
        self.assertEqual(Q.statetracker.state, [[5, 2, 1], [1, 1, 1], [0, 1, 2], [0, 0, 0]])

    def test_nodeclassmatrix_block_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.NodeClassMatrix())
        N = Q.transitive_nodes[2]
        Q.statetracker.state = [[3, 2, 1], [1, 1, 1], [3, 1, 2], [0, 0, 0]]
        self.assertEqual(Q.statetracker.state, [[3, 2, 1], [1, 1, 1], [3, 1, 2], [0, 0, 0]])
        N.block_individual(ciw.Individual(1), Q.nodes[1])
        self.assertEqual(Q.statetracker.state, [[3, 2, 1], [1, 1, 1], [3, 1, 2], [0, 0, 0]])

    def test_nodeclassmatrix_accept_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.NodeClassMatrix())
        N = Q.transitive_nodes[2]
        self.assertEqual(Q.statetracker.state, [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]])
        Q.current_time = 45.6
        N.accept(ciw.Individual(3, 2))
        self.assertEqual(Q.statetracker.state, [[0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, 0]])


class TestNaiveBlocking(unittest.TestCase):
    def test_naive_init_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NaiveBlocking()
        B.initialise(Q)
        self.assertEqual(B.simulation, Q)
        self.assertEqual(B.state, [[0, 0], [0, 0], [0, 0], [0, 0]])

    def test_naive_change_state_accept_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NaiveBlocking()
        B.initialise(Q)
        self.assertEqual(B.state, [[0, 0], [0, 0], [0, 0], [0, 0]])
        B.change_state_accept(1, 1)
        self.assertEqual(B.state, [[1, 0], [0, 0], [0, 0], [0, 0]])

    def test_naive_change_state_block_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NaiveBlocking()
        B.initialise(Q)
        B.state = [[1, 0], [0, 0], [0, 0], [0, 0]]
        B.change_state_block(1, 1, 2)
        self.assertEqual(B.state, [[0, 1], [0, 0], [0, 0], [0, 0]])

    def test_naive_change_state_release_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NaiveBlocking()
        B.initialise(Q)
        B.state = [[2, 1], [3, 0], [1, 0], [4, 4]]
        B.change_state_release(1, 1, 2, False)
        self.assertEqual(B.state, [[1, 1], [3, 0], [1, 0], [4, 4]])
        B.change_state_release(1, 1, 2, True)
        self.assertEqual(B.state, [[1, 0], [3, 0], [1, 0], [4, 4]])

    def test_naive_hash_state_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NaiveBlocking()
        B.initialise(Q)
        B.state = [[3, 4], [1, 2], [0, 1], [0, 0]]
        self.assertEqual(B.hash_state(), ((3, 4), (1, 2), (0, 1), (0, 0)))

    def test_naive_release_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.NaiveBlocking())
        N = Q.transitive_nodes[2]
        inds = [ciw.Individual(i) for i in range(5)]
        N.individuals = [inds]
        for ind in N.individuals[0]:
            srvr = N.find_free_server()
            N.attach_server(srvr, ind)
        Q.statetracker.state = [[4, 1], [3, 0], [5, 1], [0, 0]]
        self.assertEqual(Q.statetracker.state, [[4, 1], [3, 0], [5, 1], [0, 0]])
        Q.current_time = 43.11
        N.release(0, Q.nodes[1])
        self.assertEqual(Q.statetracker.state, [[5, 1], [3, 0], [4, 1], [0, 0]])
        N.all_individuals[1].is_blocked = True
        Q.current_time = 46.72
        N.release(1, Q.nodes[1])
        self.assertEqual(Q.statetracker.state, [[6, 1], [3, 0], [4, 0], [0, 0]])
        N.release(1, Q.nodes[-1])
        self.assertEqual(Q.statetracker.state, [[6, 1], [3, 0], [3, 0], [0, 0]])

    def test_naive_block_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.NaiveBlocking())
        N = Q.transitive_nodes[2]
        Q.statetracker.state = [[4, 1], [3, 0], [5, 1], [0, 0]]
        self.assertEqual(Q.statetracker.state, [[4, 1], [3, 0], [5, 1], [0, 0]])
        N.block_individual(ciw.Individual(1), Q.nodes[1])
        self.assertEqual(Q.statetracker.state, [[4, 1], [3, 0], [4, 2], [0, 0]])

    def test_naive_accept_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.NaiveBlocking())
        N = Q.transitive_nodes[2]
        self.assertEqual(Q.statetracker.state, [[0, 0], [0, 0], [0, 0], [0, 0]])
        Q.current_time = 45.6
        N.accept(ciw.Individual(3, 2))
        self.assertEqual(Q.statetracker.state, [[0, 0], [0, 0], [1, 0], [0, 0]])


class TestMatrixBlocking(unittest.TestCase):
    def test_matrix_init_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.MatrixBlocking()
        B.initialise(Q)
        self.assertEqual(B.simulation, Q)
        self.assertEqual(B.state, [[[[], [], [], []],
                                    [[], [], [], []],
                                    [[], [], [], []],
                                    [[], [], [], []]],
                                    [0, 0, 0, 0]])

    def test_matrix_change_state_accept_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.MatrixBlocking()
        B.initialise(Q)
        self.assertEqual(B.state, [[[[], [], [], []],
                                    [[], [], [], []],
                                    [[], [], [], []],
                                    [[], [], [], []]],
                                    [0, 0, 0, 0]])
        B.change_state_accept(1, 1)
        self.assertEqual(B.state, [[[[], [], [], []],
                                    [[], [], [], []],
                                    [[], [], [], []],
                                    [[], [], [], []]],
                                    [1, 0, 0, 0]])

    def test_matrix_change_state_block_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.MatrixBlocking()
        B.initialise(Q)
        B.state = [[[[], [], [], []],
                    [[], [], [], []],
                    [[], [], [], []],
                    [[], [], [], []]],
                    [2, 3, 1, 0]]
        B.change_state_block(1, 3, 2)
        self.assertEqual(B.state, [[[[], [], [1], []],
                                    [[], [], [], []],
                                    [[], [], [], []],
                                    [[], [], [], []]],
                                    [2, 3, 1, 0]])
        B.change_state_block(2, 1, 0)
        self.assertEqual(B.state, [[[[],  [], [1], []],
                                    [[2], [], [],  []],
                                    [[],  [], [],  []],
                                    [[],  [], [],  []]],
                                    [2, 3, 1, 0]])
        B.change_state_block(1, 3, 0)
        self.assertEqual(B.state, [[[[],  [], [1, 3], []],
                                    [[2], [], [],     []],
                                    [[],  [], [],     []],
                                    [[],  [], [],     []]],
                                    [2, 3, 1, 0]])

    def test_matrix_change_state_release_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.MatrixBlocking()
        B.initialise(Q)
        B.state = [[[[],  [], [1, 3], []],
                    [[2], [], [],     []],
                    [[],  [], [],     []],
                    [[],  [], [],     []]],
                    [2, 3, 1, 0]]
        B.change_state_release(3, 1, 2, False)
        self.assertEqual(B.state, [[[[],  [], [1, 3], []],
                                     [[2], [], [],     []],
                                     [[],  [], [],     []],
                                     [[],  [], [],     []]],
                                     [2, 3, 0, 0]])
        B.change_state_release(1, 3, 0, True)
        self.assertEqual(B.state, [[[[],  [], [2], []],
                                    [[1], [], [],   []],
                                    [[],  [], [],   []],
                                    [[],  [], [],   []]],
                                    [1, 3, 0, 0]])

    def test_matrix_hash_state_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.MatrixBlocking()
        B.initialise(Q)
        B.state = [[[[],  [], [1, 3], []],
                    [[2], [], [],     []],
                    [[],  [], [],     []],
                    [[],  [], [],     []]],
                    [2, 3, 0, 0]]
        self.assertEqual(B.hash_state(), ((((),   (), (1, 3), ()),
                                           ((2,), (), (),     ()),
                                           ((),   (), (),     ()),
                                           ((),   (), (),     ())),
                                           (2, 3, 0, 0)))

    def test_matrix_release_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.MatrixBlocking())
        N = Q.transitive_nodes[2]
        inds = [ciw.Individual(i) for i in range(5)]
        N.individuals = [inds]
        for ind in N.individuals[0]:
            srvr = N.find_free_server()
            N.attach_server(srvr, ind)
        Q.statetracker.state = [[[[],  [2], [], []],
                                 [[],  [],  [], []],
                                 [[1], [],  [], []],
                                 [[],  [],  [], []]],
                                 [5, 3, 6, 0]]
        Q.statetracker.increment = 3
        self.assertEqual(Q.statetracker.state, [[[[],  [2], [], []],
                                                 [[],  [],  [], []],
                                                 [[1], [],  [], []],
                                                 [[],  [],  [], []]],
                                                 [5, 3, 6, 0]])
        Q.current_time = 43.11
        N.release(0, Q.nodes[1])
        self.assertEqual(Q.statetracker.state, [[[[],  [2], [], []],
                                                 [[],  [],  [], []],
                                                 [[1], [],  [], []],
                                                 [[],  [],  [], []]],
                                                 [6, 3, 5, 0]])
        N.all_individuals[1].is_blocked = True
        Q.current_time = 46.72
        N.release(1, Q.nodes[1])
        self.assertEqual(Q.statetracker.state, [[[[], [1], [], []],
                                                 [[], [],  [], []],
                                                 [[], [],  [], []],
                                                 [[], [],  [], []]],
                                                 [7, 3, 4, 0]])
        Q.current_time = 48.39
        N.release(1, Q.nodes[-1])
        self.assertEqual(Q.statetracker.state, [[[[], [1], [], []],
                                                 [[], [],  [], []],
                                                 [[], [],  [], []],
                                                 [[], [],  [], []]],
                                                 [7, 3, 3, 0]])

    def test_matrix_block_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.MatrixBlocking())
        N = Q.transitive_nodes[2]
        Q.statetracker.state = [[[[],  [2], [], []],
                                 [[],  [],  [], []],
                                 [[1], [],  [], []],
                                 [[],  [],  [], []]],
                                 [5, 3, 6, 0]]
        Q.statetracker.increment = 3
        self.assertEqual(Q.statetracker.state, [[[[],  [2], [], []],
                                                 [[],  [],  [], []],
                                                 [[1], [],  [], []],
                                                 [[],  [],  [], []]],
                                                 [5, 3, 6, 0]])
        N.block_individual(ciw.Individual(1), Q.nodes[1])
        self.assertEqual(Q.statetracker.state, [[[[],     [2], [], []],
                                                 [[],     [],  [], []],
                                                 [[1, 3], [],  [], []],
                                                 [[],     [],  [], []]],
                                                 [5, 3, 6, 0]])

    def test_matrix_accept_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.MatrixBlocking())
        N = Q.transitive_nodes[2]
        self.assertEqual(Q.statetracker.state, [[[[], [], [], []],
                                                 [[], [], [], []],
                                                 [[], [], [], []],
                                                 [[], [], [], []]],
                                                 [0, 0, 0, 0]])
        Q.current_time = 45.6
        N.accept(ciw.Individual(3, 2))
        self.assertEqual(Q.statetracker.state, [[[[], [], [], []],
                                                 [[], [], [], []],
                                                 [[], [], [], []],
                                                 [[], [], [], []]],
                                                 [0, 0, 1, 0]])


class TestTrackHistory(unittest.TestCase):
    def test_one_node_deterministic_naiveblocking(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1.5, 0.3, 2.4, 1.1])],
            service_distributions=[ciw.dists.Sequential([1.8, 2.2, 0.2, 0.2, 0.2, 0.2])],
            number_of_servers=[1]
        )
        B = ciw.trackers.NaiveBlocking()
        Q = ciw.Simulation(N, tracker=B, exact=26)
        Q.simulate_until_max_time(15.5)
        expected_history = [
        [Decimal('0.0'), ((0, 0),)],
        [Decimal('1.5'), ((1, 0),)],
        [Decimal('1.8'), ((2, 0),)],
        [Decimal('3.3'), ((1, 0),)],
        [Decimal('4.2'), ((2, 0),)],
        [Decimal('5.3'), ((3, 0),)],
        [Decimal('5.5'), ((2, 0),)],
        [Decimal('5.7'), ((1, 0),)],
        [Decimal('5.9'), ((0, 0),)],
        [Decimal('6.8'), ((1, 0),)],
        [Decimal('7.0'), ((0, 0),)],
        [Decimal('7.1'), ((1, 0),)],
        [Decimal('7.3'), ((0, 0),)],
        [Decimal('9.5'), ((1, 0),)],
        [Decimal('10.6'), ((2, 0),)],
        [Decimal('11.3'), ((1, 0),)],
        [Decimal('12.1'), ((2, 0),)],
        [Decimal('12.4'), ((3, 0),)],
        [Decimal('13.5'), ((2, 0),)],
        [Decimal('13.7'), ((1, 0),)],
        [Decimal('13.9'), ((0, 0),)],
        [Decimal('14.8'), ((1, 0),)],
        [Decimal('15.0'), ((0, 0),)]
        ]
        self.assertEqual(Q.statetracker.history, expected_history)

    def test_one_node_deterministic_systempopulation(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1.5, 0.3, 2.4, 1.1])],
            service_distributions=[ciw.dists.Sequential([1.8, 2.2, 0.2, 0.2, 0.2, 0.2])],
            number_of_servers=[1]
        )
        B = ciw.trackers.SystemPopulation()
        Q = ciw.Simulation(N, tracker=B, exact=26)
        Q.simulate_until_max_time(15.5)
        expected_history = [
        [Decimal('0.0'), 0],
        [Decimal('1.5'), 1],
        [Decimal('1.8'), 2],
        [Decimal('3.3'), 1],
        [Decimal('4.2'), 2],
        [Decimal('5.3'), 3],
        [Decimal('5.5'), 2],
        [Decimal('5.7'), 1],
        [Decimal('5.9'), 0],
        [Decimal('6.8'), 1],
        [Decimal('7.0'), 0],
        [Decimal('7.1'), 1],
        [Decimal('7.3'), 0],
        [Decimal('9.5'), 1],
        [Decimal('10.6'), 2],
        [Decimal('11.3'), 1],
        [Decimal('12.1'), 2],
        [Decimal('12.4'), 3],
        [Decimal('13.5'), 2],
        [Decimal('13.7'), 1],
        [Decimal('13.9'), 0],
        [Decimal('14.8'), 1],
        [Decimal('15.0'), 0]
        ]
        self.assertEqual(Q.statetracker.history, expected_history)


    def test_one_node_deterministic_nodepopulation(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1.5, 0.3, 2.4, 1.1])],
            service_distributions=[ciw.dists.Sequential([1.8, 2.2, 0.2, 0.2, 0.2, 0.2])],
            number_of_servers=[1]
        )
        B = ciw.trackers.NodePopulation()
        Q = ciw.Simulation(N, tracker=B, exact=26)
        Q.simulate_until_max_time(15.5)
        expected_history = [
        [Decimal('0.0'), (0,)],
        [Decimal('1.5'), (1,)],
        [Decimal('1.8'), (2,)],
        [Decimal('3.3'), (1,)],
        [Decimal('4.2'), (2,)],
        [Decimal('5.3'), (3,)],
        [Decimal('5.5'), (2,)],
        [Decimal('5.7'), (1,)],
        [Decimal('5.9'), (0,)],
        [Decimal('6.8'), (1,)],
        [Decimal('7.0'), (0,)],
        [Decimal('7.1'), (1,)],
        [Decimal('7.3'), (0,)],
        [Decimal('9.5'), (1,)],
        [Decimal('10.6'), (2,)],
        [Decimal('11.3'), (1,)],
        [Decimal('12.1'), (2,)],
        [Decimal('12.4'), (3,)],
        [Decimal('13.5'), (2,)],
        [Decimal('13.7'), (1,)],
        [Decimal('13.9'), (0,)],
        [Decimal('14.8'), (1,)],
        [Decimal('15.0'), (0,)]
        ]
        self.assertEqual(Q.statetracker.history, expected_history)

    def test_one_node_deterministic_nodeclassmatrix(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1.5, 0.3, 2.4, 1.1])],
            service_distributions=[ciw.dists.Sequential([1.8, 2.2, 0.2, 0.2, 0.2, 0.2])],
            number_of_servers=[1]
        )
        B = ciw.trackers.NodeClassMatrix()
        Q = ciw.Simulation(N, tracker=B, exact=26)
        Q.simulate_until_max_time(15.5)
        expected_history = [
        [Decimal('0.0'), ((0,),)],
        [Decimal('1.5'), ((1,),)],
        [Decimal('1.8'), ((2,),)],
        [Decimal('3.3'), ((1,),)],
        [Decimal('4.2'), ((2,),)],
        [Decimal('5.3'), ((3,),)],
        [Decimal('5.5'), ((2,),)],
        [Decimal('5.7'), ((1,),)],
        [Decimal('5.9'), ((0,),)],
        [Decimal('6.8'), ((1,),)],
        [Decimal('7.0'), ((0,),)],
        [Decimal('7.1'), ((1,),)],
        [Decimal('7.3'), ((0,),)],
        [Decimal('9.5'), ((1,),)],
        [Decimal('10.6'), ((2,),)],
        [Decimal('11.3'), ((1,),)],
        [Decimal('12.1'), ((2,),)],
        [Decimal('12.4'), ((3,),)],
        [Decimal('13.5'), ((2,),)],
        [Decimal('13.7'), ((1,),)],
        [Decimal('13.9'), ((0,),)],
        [Decimal('14.8'), ((1,),)],
        [Decimal('15.0'), ((0,),)]
        ]
        self.assertEqual(Q.statetracker.history, expected_history)
