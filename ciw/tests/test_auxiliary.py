import unittest
import ciw
import random
from collections import Counter
from hypothesis import given
from hypothesis.strategies import (floats, integers, lists, random_module)

class TestAuxiliary(unittest.TestCase):
    def test_seed(self):
        ciw.seed(5)
        a1 = random.expovariate(5)
        b1 = ciw.random_choice([4, 5, 6, 1])
        c1 = random.random()
        ciw.seed(5)
        a2 = random.expovariate(5)
        b2 = ciw.random_choice([4, 5, 6, 1])
        c2 = random.random()
        self.assertEqual(a1, a2)
        self.assertEqual(b1, b2)
        self.assertEqual(c1, c2)

    @given(choices=lists(integers(min_value=0, max_value=10000), min_size=1, max_size=100),
           lmbda=floats(min_value=0.0001, max_value=10000),
           s=integers(min_value=0, max_value=10000),
           rm=random_module())
    def test_seedh(self, choices, lmbda, s, rm):
        ciw.seed(s)
        a1 = random.expovariate(lmbda)
        b1 = ciw.random_choice(choices)
        c1 = random.random()
        ciw.seed(s)
        a2 = random.expovariate(lmbda)
        b2 = ciw.random_choice(choices)
        c2 = random.random()
        self.assertEqual(a1, a2)
        self.assertEqual(b1, b2)
        self.assertEqual(c1, c2)

    def test_randomchoice(self):
        ciw.seed(1)
        array = [1, 2, 3, 4, 5, 6, 7, 8]
        probs = [0.4, 0.2, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05]
        choices = [ciw.random_choice(array, probs) for _ in range(200)]
        choice_counts = Counter(choices)
        self.assertEqual(choice_counts, {1:79, 2:49, 3:14, 4:22, 5:11, 6:11, 7:5, 8:9})

        ciw.seed(2)
        array = ['A', 'B', 'C', 'Ch', 'D', 'Dd', 'E', 'F', 'Ff', 'G', 'Ng', 'H']
        probs = [0.0, 0.1, 0.0, 0.3, 0.0, 0.2, 0.0, 0.1, 0.1, 0.0, 0.2, 0.0]
        choices = [ciw.random_choice(array, probs) for _ in range(300)]
        choice_counts = Counter(choices)
        self.assertEqual(choice_counts, {'B':34, 'Ch':83, 'Dd':68, 'F':26, 'Ff':31, 'Ng':58})

        ciw.seed(3)
        array = 'Geraint'
        probs = [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        choices = [ciw.random_choice(array, probs) for _ in range(100)]
        choice_counts = Counter(choices)
        self.assertEqual(choice_counts, {'i':100})

        ciw.seed(4)
        array = [111, 222, 333, 444]
        choices = [ciw.random_choice(array) for _ in range(800)]
        choice_counts = Counter(choices)
        self.assertEqual(choice_counts, {111: 209, 222: 186, 333: 180, 444: 225})

        # Test that no random numbers used in this case:
        ciw.seed(5)
        r1 = random.random()
        ciw.seed(5)
        array = ['Node 1', 'Node 2', 'Exit Node']
        probs = [0.0, 0.0, 1.0]
        choices = [ciw.random_choice(array, probs) for _ in range(100)]
        r2 = random.random()
        choice_counts = Counter(choices)
        self.assertEqual(choice_counts, {'Exit Node': 100})
        self.assertEqual(r1, r2)

    def test_flatten_list(self):
        for seed in range(20):
            random.seed(seed)
            all_classes = [[random.random() for _ in range(random.randrange(3, 30, 1))] for _ in range(random.randrange(5, 20, 1))]
            A = [i for priority in all_classes for i in priority]
            B = ciw.flatten_list(all_classes)
            self.assertEqual(A, B)

    def test_no_routing(self):
        ind = ciw.Individual(22)
        self.assertEqual(ciw.no_routing(ind), [])
