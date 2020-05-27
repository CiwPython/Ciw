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


    def test_two_node_deterministic_nodepopulationsubset(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(0.31), ciw.dists.Deterministic(0.71)],
            service_distributions=[ciw.dists.Deterministic(1), ciw.dists.Deterministic(1)],
            routing=[[0.0, 1.0], [0.0, 0.0]],
            number_of_servers=[1, 1]
        )

        # First with Both nodes
        B = ciw.trackers.NodePopulationSubset([0, 1])
        Q = ciw.Simulation(N, tracker=B, exact=26)
        Q.simulate_until_max_time(4.5)
        expected_history = [
        [Decimal('0.0'), (0, 0)],
        [Decimal('0.31'), (1, 0)],
        [Decimal('0.62'), (2, 0)],
        [Decimal('0.71'), (2, 1)],
        [Decimal('0.93'), (3, 1)],
        [Decimal('1.24'), (4, 1)],
        [Decimal('1.31'), (3, 2)],
        [Decimal('1.42'), (3, 3)],
        [Decimal('1.55'), (4, 3)],
        [Decimal('1.71'), (4, 2)],
        [Decimal('1.86'), (5, 2)],
        [Decimal('2.13'), (5, 3)],
        [Decimal('2.17'), (6, 3)],
        [Decimal('2.31'), (5, 4)],
        [Decimal('2.48'), (6, 4)],
        [Decimal('2.71'), (6, 3)],
        [Decimal('2.79'), (7, 3)],
        [Decimal('2.84'), (7, 4)],
        [Decimal('3.10'), (8, 4)],
        [Decimal('3.31'), (7, 5)],
        [Decimal('3.41'), (8, 5)],
        [Decimal('3.55'), (8, 6)],
        [Decimal('3.71'), (8, 5)],
        [Decimal('3.72'), (9, 5)],
        [Decimal('4.03'), (10, 5)],
        [Decimal('4.26'), (10, 6)],
        [Decimal('4.31'), (9, 7)],
        [Decimal('4.34'), (10, 7)]
        ]
        self.assertEqual(Q.statetracker.history, expected_history)

        # First with then 1st only
        B = ciw.trackers.NodePopulationSubset([0])
        Q = ciw.Simulation(N, tracker=B, exact=26)
        Q.simulate_until_max_time(4.5)
        expected_history = [
        [Decimal('0.0'), (0,)],
        [Decimal('0.31'), (1,)],
        [Decimal('0.62'), (2,)],
        [Decimal('0.93'), (3,)],
        [Decimal('1.24'), (4,)],
        [Decimal('1.31'), (3,)],
        [Decimal('1.55'), (4,)],
        [Decimal('1.86'), (5,)],
        [Decimal('2.17'), (6,)],
        [Decimal('2.31'), (5,)],
        [Decimal('2.48'), (6,)],
        [Decimal('2.79'), (7,)],
        [Decimal('3.10'), (8,)],
        [Decimal('3.31'), (7,)],
        [Decimal('3.41'), (8,)],
        [Decimal('3.72'), (9,)],
        [Decimal('4.03'), (10,)],
        [Decimal('4.31'), (9,)],
        [Decimal('4.34'), (10,)]
        ]
        self.assertEqual(Q.statetracker.history, expected_history)

        # Then 2nd only
        B = ciw.trackers.NodePopulationSubset([1])
        Q = ciw.Simulation(N, tracker=B, exact=26)
        Q.simulate_until_max_time(4.5)
        expected_history = [
        [Decimal('0.0'), (0,)],
        [Decimal('0.71'), (1,)],
        [Decimal('1.31'), (2,)],
        [Decimal('1.42'), (3,)],
        [Decimal('1.71'), (2,)],
        [Decimal('2.13'), (3,)],
        [Decimal('2.31'), (4,)],
        [Decimal('2.71'), (3,)],
        [Decimal('2.84'), (4,)],
        [Decimal('3.31'), (5,)],
        [Decimal('3.55'), (6,)],
        [Decimal('3.71'), (5,)],
        [Decimal('4.26'), (6,)],
        [Decimal('4.31'), (7,)]
        ]
        self.assertEqual(Q.statetracker.history, expected_history)

    def test_no_state_change_when_blocking_subset(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Deterministic(1), ciw.dists.NoArrivals()],
            service_distributions=[ciw.dists.Deterministic(0.1), ciw.dists.Deterministic(1.2)],
            number_of_servers=[1, 1],
            routing=[[0.0, 1.0], [0.0, 0.0]],
            queue_capacities=[float('Inf'), 0]
        )
        B = ciw.trackers.NodePopulationSubset([1])
        Q = ciw.Simulation(N, tracker=B, exact=26)
        Q.simulate_until_max_time(15.5)
        expected_history = [
        [Decimal('0.0'), (0,)],
        [Decimal('1.1'), (1,)]
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

    def test_track_history_two_node_two_class(self):
        N = ciw.create_network(
            arrival_distributions={
                'Class 0': [ciw.dists.Exponential(0.5), ciw.dists.Exponential(0.5)],
                'Class 1': [ciw.dists.Exponential(0.5), ciw.dists.Exponential(0.5)]},
            service_distributions={
                'Class 0': [ciw.dists.Exponential(1), ciw.dists.Exponential(1)],
                'Class 1': [ciw.dists.Exponential(1), ciw.dists.Exponential(1)]},
            number_of_servers=[1, 1],
            routing={
                'Class 0': [[0.2, 0.2], [0.2, 0.2]],
                'Class 1': [[0.2, 0.2], [0.2, 0.2]]}
        )
        
        # System Population
        ciw.seed(0)
        Q = ciw.Simulation(N, tracker=ciw.trackers.SystemPopulation())
        Q.simulate_until_max_time(5)
        observed_history = Q.statetracker.history
        expected_history = [
            [0.00, 0],
            [0.60, 1],
            [1.09, 2],
            [1.64, 3],
            [1.96, 2],
            [2.84, 3],
            [3.39, 4],
            [3.41, 5],
            [3.72, 6],
            [3.80, 5],
            [4.07, 4],
            [4.15, 5],
            [4.17, 4],
            [4.28, 3]
        ]
        self.assertEqual(len(observed_history), len(expected_history))
        for obs, exp in zip(observed_history, expected_history):
            self.assertEqual([round(obs[0], 2), obs[1]], exp)

        # Node Population
        ciw.seed(0)
        Q = ciw.Simulation(N, tracker=ciw.trackers.NodePopulation())
        Q.simulate_until_max_time(5)
        observed_history = Q.statetracker.history
        expected_history = [
            [0.00, (0, 0)],
            [0.60, (0, 1)],
            [1.09, (0, 2)],
            [1.64, (0, 3)],
            [1.96, (0, 2)],
            [2.84, (1, 2)],
            [3.39, (1, 3)],
            [3.41, (2, 3)],
            [3.72, (3, 3)],
            [3.80, (2, 3)],
            [4.07, (2, 2)],
            [4.15, (2, 3)],
            [4.17, (1, 3)],
            [4.28, (0, 3)]
        ]
        self.assertEqual(len(observed_history), len(expected_history))
        for obs, exp in zip(observed_history, expected_history):
            self.assertEqual([round(obs[0], 2), obs[1]], exp)

        # Node Class Matrix
        ciw.seed(0)
        Q = ciw.Simulation(N, tracker=ciw.trackers.NodeClassMatrix())
        Q.simulate_until_max_time(5)
        observed_history = Q.statetracker.history
        expected_history = [
            [0.00, ((0, 0), (0, 0))],
            [0.60, ((0, 0), (0, 1))],
            [1.09, ((0, 0), (1, 1))],
            [1.64, ((0, 0), (1, 2))],
            [1.96, ((0, 0), (0, 2))],
            [2.84, ((0, 1), (0, 2))],
            [3.39, ((0, 1), (0, 3))],
            [3.41, ((0, 2), (0, 3))],
            [3.72, ((1, 2), (0, 3))],
            [3.80, ((1, 1), (0, 3))],
            [4.07, ((1, 1), (0, 2))],
            [4.15, ((1, 1), (1, 2))],
            [4.17, ((1, 0), (1, 2))],
            [4.28, ((0, 0), (1, 2))]
        ]
        self.assertEqual(len(observed_history), len(expected_history))
        for obs, exp in zip(observed_history, expected_history):
            self.assertEqual([round(obs[0], 2), obs[1]], exp)


class TestStateProbabilities(unittest.TestCase):
    def test_prob_one_node_deterministic_naiveblocking(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1.5, 0.3, 2.4, 1.1])],
            service_distributions=[ciw.dists.Sequential([1.8, 2.2, 0.2, 0.2, 0.2, 0.2])],
            number_of_servers=[1]
        )
        B = ciw.trackers.NaiveBlocking()
        Q = ciw.Simulation(N, tracker=B, exact=26)
        Q.simulate_until_max_time(15.5)
        expected_probabilities = {
            ((0, 0),): Decimal('0.38157894736842105263157895'),
            ((1, 0),): Decimal('0.26973684210526315789473684'),
            ((2, 0),): Decimal('0.26315789473684210526315789'),
            ((3, 0),): Decimal('0.085526315789473684210526316')
            }
        
        expected_probabilities_with_time_period = {
            ((2, 0),): Decimal('0.1'),
            ((3, 0),): Decimal('0.04'),
            ((1, 0),): Decimal('0.22'),
            ((0, 0),): Decimal('0.64')
            }

        for state in expected_probabilities:
            self.assertEqual(
                Q.statetracker.state_probabilities()[state], 
                expected_probabilities[state]
                )
        
        for state in expected_probabilities_with_time_period:
            self.assertEqual(
                Q.statetracker.state_probabilities(observation_period=(5,10))[state], 
                expected_probabilities_with_time_period[state]
                )

    def test_prob_one_node_deterministic_systempopulation(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1.5, 0.3, 2.4, 1.1])],
            service_distributions=[ciw.dists.Sequential([1.8, 2.2, 0.2, 0.2, 0.2, 0.2])],
            number_of_servers=[1]
        )
        B = ciw.trackers.SystemPopulation()
        Q = ciw.Simulation(N, tracker=B, exact=26)
        Q.simulate_until_max_time(15.5)
        expected_probabilities = {
            0: Decimal('0.38157894736842105263157895'),
            1: Decimal('0.26973684210526315789473684'),
            2: Decimal('0.26315789473684210526315789'),
            3: Decimal('0.085526315789473684210526316')
            }
        expected_probabilities_with_time_period = {
            2: Decimal('0.1'), 
            3: Decimal('0.04'), 
            1: Decimal('0.22'), 
            0: Decimal('0.64')
            }
            
        for state in expected_probabilities:
            self.assertEqual(
                Q.statetracker.state_probabilities()[state], 
                expected_probabilities[state]
                )
        
        for state in expected_probabilities_with_time_period:
            self.assertEqual(
                Q.statetracker.state_probabilities(observation_period=(5,10))[state], 
                expected_probabilities_with_time_period[state]
                )

    def test_prob_one_node_deterministic_nodepopulation(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1.5, 0.3, 2.4, 1.1])],
            service_distributions=[ciw.dists.Sequential([1.8, 2.2, 0.2, 0.2, 0.2, 0.2])],
            number_of_servers=[1]
        )
        B = ciw.trackers.NodePopulation()
        Q = ciw.Simulation(N, tracker=B, exact=26)
        Q.simulate_until_max_time(15.5)
        expected_probabilities = {
            (0,): Decimal('0.38157894736842105263157895'),
            (1,): Decimal('0.26973684210526315789473684'),
            (2,): Decimal('0.26315789473684210526315789'),
            (3,): Decimal('0.085526315789473684210526316')
            }
        expected_probabilities_with_time_period = {
            (2,): Decimal('0.1'),
            (3,): Decimal('0.04'),
            (1,): Decimal('0.22'),
            (0,): Decimal('0.64')
            }
        for state in expected_probabilities:
            self.assertEqual(
                Q.statetracker.state_probabilities()[state], 
                expected_probabilities[state]
                )
        
        for state in expected_probabilities_with_time_period:
            self.assertEqual(
                Q.statetracker.state_probabilities(observation_period=(5,10))[state], 
                expected_probabilities_with_time_period[state]
                )

    def test_prob_one_node_deterministic_nodeclassmatrix(self):
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Sequential([1.5, 0.3, 2.4, 1.1])],
            service_distributions=[ciw.dists.Sequential([1.8, 2.2, 0.2, 0.2, 0.2, 0.2])],
            number_of_servers=[1]
        )
        B = ciw.trackers.NodeClassMatrix()
        Q = ciw.Simulation(N, tracker=B, exact=26)
        Q.simulate_until_max_time(15.5)
        expected_probabilities = {
            ((0,),): Decimal('0.38157894736842105263157895'),
            ((1,),): Decimal('0.26973684210526315789473684'),
            ((2,),): Decimal('0.26315789473684210526315789'),
            ((3,),): Decimal('0.085526315789473684210526316')
            }
        expected_probabilities_with_time_period = {
            ((2,),): Decimal('0.1'),
            ((3,),): Decimal('0.04'),
            ((1,),): Decimal('0.22'),
            ((0,),): Decimal('0.64')
            }
        for state in expected_probabilities:
            self.assertEqual(
                Q.statetracker.state_probabilities()[state], 
                expected_probabilities[state]
                )
        
        for state in expected_probabilities_with_time_period:
            self.assertEqual(
                Q.statetracker.state_probabilities(observation_period=(5,10))[state], 
                expected_probabilities_with_time_period[state]
                )

    def test_prob_track_history_two_node_two_class(self):
        N = ciw.create_network(
            arrival_distributions={
                'Class 0': [ciw.dists.Exponential(0.5), ciw.dists.Exponential(0.5)],
                'Class 1': [ciw.dists.Exponential(0.5), ciw.dists.Exponential(0.5)]},
            service_distributions={
                'Class 0': [ciw.dists.Exponential(1), ciw.dists.Exponential(1)],
                'Class 1': [ciw.dists.Exponential(1), ciw.dists.Exponential(1)]},
            number_of_servers=[1, 1],
            routing={
                'Class 0': [[0.2, 0.2], [0.2, 0.2]],
                'Class 1': [[0.2, 0.2], [0.2, 0.2]]}
        )
        
        # System Population
        ciw.seed(0)
        Q = ciw.Simulation(N, tracker=ciw.trackers.SystemPopulation())
        Q.simulate_until_max_time(5)
        expected_probabilities = {
            0: 0.1366944915680613,
            1: 0.11225559969470539,
            2: 0.3240424959070235,
            3: 0.22414907894503974,
            4: 0.04813145483931205,
            5: 0.13662855193885537,
            6: 0.018098327107002654
            }
        expected_probabilities_with_time_period = {
            1: 0.030475430361061855,
            2: 0.47354672264790626,
            3: 0.2921852718539804,
            4: 0.008450291962042685,
            5: 0.16889388953780524,
            6: 0.026448393637203527
            }
        
        for state in expected_probabilities:
            self.assertEqual(
                Q.statetracker.state_probabilities()[state], 
                expected_probabilities[state]
                )
        
        for state in expected_probabilities_with_time_period:
            self.assertEqual(
                Q.statetracker.state_probabilities(observation_period=(1, 4))[state], 
                expected_probabilities_with_time_period[state]
                )

        # Node Population
        ciw.seed(0)
        Q = ciw.Simulation(N, tracker=ciw.trackers.NodePopulation())
        Q.simulate_until_max_time(5)
        expected_probabilities = {
            (0, 0): 0.1366944915680613,
            (0, 1): 0.11225559969470539,
            (0, 2): 0.3240424959070235,
            (0, 3): 0.0983851025458379,
            (1, 2): 0.12576397639920184,
            (1, 3): 0.02999254345852149,
            (2, 3): 0.13662855193885537,
            (3, 3): 0.018098327107002654,
            (2, 2): 0.018138911380790552
            }
        expected_probabilities_with_time_period = {
            (0, 1): 0.030475430361061855,
            (0, 2): 0.47354672264790626,
            (0, 3): 0.10839728230553976,
            (1, 2): 0.18378798954844067,
            (1, 3): 0.008450291962042685,
            (2, 3): 0.16889388953780524,
            (3, 3): 0.026448393637203527
            }

        for state in expected_probabilities:
            self.assertEqual(
                Q.statetracker.state_probabilities()[state], 
                expected_probabilities[state]
                )
        
        for state in expected_probabilities_with_time_period:
            self.assertEqual(
                Q.statetracker.state_probabilities(observation_period=(1,4))[state], 
                expected_probabilities_with_time_period[state]
                )

        # Node Class Matrix
        ciw.seed(0)
        Q = ciw.Simulation(N, tracker=ciw.trackers.NodeClassMatrix())
        Q.simulate_until_max_time(5)

        expected_probabilities = {((0, 0), (0, 0)): 0.1366944915680613,
            ((0, 0), (0, 1)): 0.11225559969470539,
            ((0, 0), (1, 1)): 0.12454611130253443,
            ((0, 0), (1, 2)): 0.0983851025458379,
            ((0, 0), (0, 2)): 0.19949638460448907,
            ((0, 1), (0, 2)): 0.12576397639920184,
            ((0, 1), (0, 3)): 0.005782436172743465,
            ((0, 2), (0, 3)): 0.07008049325290676,
            ((1, 2), (0, 3)): 0.018098327107002654,
            ((1, 1), (0, 3)): 0.06259720833539882,
            ((1, 1), (0, 2)): 0.018138911380790552,
            ((1, 1), (1, 2)): 0.003950850350549779,
            ((1, 0), (1, 2)): 0.024210107285778028
            }
        expected_probabilities_with_time_period = {
            ((0, 0), (0, 1)): 0.030475430361061855,
            ((0, 0), (1, 1)): 0.18200823524942553,
            ((0, 0), (1, 2)): 0.10839728230553976,
            ((0, 0), (0, 2)): 0.29153848739848076,
            ((0, 1), (0, 2)): 0.18378798954844067,
            ((0, 1), (0, 3)): 0.008450291962042685,
            ((0, 2), (0, 3)): 0.10241369055182432,
            ((1, 2), (0, 3)): 0.026448393637203527,
            ((1, 1), (0, 3)): 0.0664801989859809
            }

        for state in expected_probabilities:
            self.assertEqual(
                Q.statetracker.state_probabilities()[state], 
                expected_probabilities[state]
                )
        
        for state in expected_probabilities_with_time_period:
            self.assertEqual(
                Q.statetracker.state_probabilities(observation_period=(1,4))[state], 
                expected_probabilities_with_time_period[state]
                )

    def test_compare_state_probabilities_to_analytical(self):
        #Example: λ = 1, μ = 3
        lamda = 1
        mu = 3
        ciw.seed(0)
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(lamda)],
            service_distributions=[ciw.dists.Exponential(mu)],
            number_of_servers=[1]
        )
        Q = ciw.Simulation(N, tracker=ciw.trackers.SystemPopulation())
        Q.simulate_until_max_time(20000)
        state_probs = Q.statetracker.state_probabilities(observation_period=(500, 20000))

        vec = [(lamda/mu)**i for i in sorted(state_probs.keys())]
        expected_probs = [v / sum(vec) for v in vec]

        for state in state_probs:
            self.assertEqual(round(state_probs[state], 2), round(expected_probs[state], 2))

        error_squared = sum([(state_probs[i] - expected_probs[i])**2 for i in sorted(state_probs.keys())])
        self.assertEqual(round(error_squared, 4), 0)


         #Example: λ = 1, μ = 4
        lamda = 1
        mu = 4
        ciw.seed(0)
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(lamda)],
            service_distributions=[ciw.dists.Exponential(mu)],
            number_of_servers=[1]
        )
        Q = ciw.Simulation(N, tracker=ciw.trackers.SystemPopulation())
        Q.simulate_until_max_time(20000)
        state_probs = Q.statetracker.state_probabilities(observation_period=(500, 20000))

        vec = [(lamda/mu)**i for i in sorted(state_probs.keys())]
        expected_probs = [v / sum(vec) for v in vec]

        for state in state_probs:
            self.assertEqual(round(state_probs[state], 2), round(expected_probs[state], 2))

        error_squared = sum([(state_probs[i] - expected_probs[i])**2 for i in sorted(state_probs.keys())])
        self.assertEqual(round(error_squared, 4), 0)


         #Example: λ = 1, μ = 5
        lamda = 1
        mu = 5
        ciw.seed(0)
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(lamda)],
            service_distributions=[ciw.dists.Exponential(mu)],
            number_of_servers=[1]
        )
        Q = ciw.Simulation(N, tracker=ciw.trackers.SystemPopulation())
        Q.simulate_until_max_time(20000)
        state_probs = Q.statetracker.state_probabilities(observation_period=(500, 20000))

        vec = [(lamda/mu)**i for i in sorted(state_probs.keys())]
        expected_probs = [v / sum(vec) for v in vec]

        for state in state_probs:
            self.assertEqual(round(state_probs[state], 2), round(expected_probs[state], 2))

        error_squared = sum([(state_probs[i] - expected_probs[i])**2 for i in sorted(state_probs.keys())])
        self.assertEqual(round(error_squared, 4), 0)

    def test_error_checking_for_state_probabilities(self):
        ciw.seed(0)
        N = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(1)],
            service_distributions=[ciw.dists.Exponential(2)],
            number_of_servers=[1]
        )
        Q = ciw.Simulation(N, tracker=ciw.trackers.SystemPopulation())
        Q.simulate_until_max_time(10)

        self.assertRaises(ValueError, Q.statetracker.state_probabilities, (-1, 5))
        self.assertRaises(ValueError, Q.statetracker.state_probabilities, (4, 2))
        self.assertRaises(ValueError, Q.statetracker.state_probabilities, (-1, -4))
        self.assertRaises(ValueError, Q.statetracker.state_probabilities, (3, 3))