import unittest
import ciw

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




class TestNaiveTracker(unittest.TestCase):
    def test_naive_init_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NaiveTracker()
        B.initialise(Q)
        self.assertEqual(B.simulation, Q)
        self.assertEqual(B.state, [[0, 0], [0, 0], [0, 0], [0, 0]])

    def test_naive_change_state_accept_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NaiveTracker()
        B.initialise(Q)
        self.assertEqual(B.state, [[0, 0], [0, 0], [0, 0], [0, 0]])
        B.change_state_accept(1, 1)
        self.assertEqual(B.state, [[1, 0], [0, 0], [0, 0], [0, 0]])

    def test_naive_change_state_block_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NaiveTracker()
        B.initialise(Q)
        B.state = [[1, 0], [0, 0], [0, 0], [0, 0]]
        B.change_state_block(1, 1, 2)
        self.assertEqual(B.state, [[0, 1], [0, 0], [0, 0], [0, 0]])

    def test_naive_change_state_release_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NaiveTracker()
        B.initialise(Q)
        B.state = [[2, 1], [3, 0], [1, 0], [4, 4]]
        B.change_state_release(1, 1, 2, False)
        self.assertEqual(B.state, [[1, 1], [3, 0], [1, 0], [4, 4]])
        B.change_state_release(1, 1, 2, True)
        self.assertEqual(B.state, [[1, 0], [3, 0], [1, 0], [4, 4]])

    def test_naive_hash_state_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.NaiveTracker()
        B.initialise(Q)
        B.state = [[3, 4], [1, 2], [0, 1], [0, 0]]
        self.assertEqual(B.hash_state(), ((3, 4), (1, 2), (0, 1), (0, 0)))

    def test_naive_release_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.NaiveTracker())
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
        Q = ciw.Simulation(params, tracker=ciw.trackers.NaiveTracker())
        N = Q.transitive_nodes[2]
        Q.statetracker.state = [[4, 1], [3, 0], [5, 1], [0, 0]]
        self.assertEqual(Q.statetracker.state, [[4, 1], [3, 0], [5, 1], [0, 0]])
        N.block_individual(ciw.Individual(1), Q.nodes[1])
        self.assertEqual(Q.statetracker.state, [[4, 1], [3, 0], [4, 2], [0, 0]])

    def test_naive_accept_method_within_simulation(self):
        params = ciw.create_network_from_yml(
            'ciw/tests/testing_parameters/params.yml')
        Q = ciw.Simulation(params, tracker=ciw.trackers.NaiveTracker())
        N = Q.transitive_nodes[2]
        self.assertEqual(Q.statetracker.state, [[0, 0], [0, 0], [0, 0], [0, 0]])
        Q.current_time = 45.6
        N.accept(ciw.Individual(3, 2))
        self.assertEqual(Q.statetracker.state, [[0, 0], [0, 0], [1, 0], [0, 0]])



class TestMatrixTracker(unittest.TestCase):
    def test_matrix_init_method(self):
        Q = ciw.Simulation(ciw.create_network_from_yml(
          'ciw/tests/testing_parameters/params.yml'))
        B = ciw.trackers.MatrixTracker()
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
        B = ciw.trackers.MatrixTracker()
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
        B = ciw.trackers.MatrixTracker()
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
        B = ciw.trackers.MatrixTracker()
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
        B = ciw.trackers.MatrixTracker()
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
        Q = ciw.Simulation(params, tracker=ciw.trackers.MatrixTracker())
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
        Q = ciw.Simulation(params, tracker=ciw.trackers.MatrixTracker())
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
        Q = ciw.Simulation(params, tracker=ciw.trackers.MatrixTracker())
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
