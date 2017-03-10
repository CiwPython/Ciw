import unittest
import ciw
import random
import numpy.random as nprandom
from collections import Counter
from hypothesis import given
from hypothesis.strategies import (floats, integers, lists, random_module)

class TestAuxiliary(unittest.TestCase):

    def test_seed(self):
        ciw.seed(5)
        a1 = random.expovariate(5)
        b1 = nprandom.choice([4, 5, 6, 1])
        c1 = random.random()
        ciw.seed(5)
        a2 = random.expovariate(5)
        b2 = nprandom.choice([4, 5, 6, 1])
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
        b1 = nprandom.choice(choices)
        c1 = random.random()
        ciw.seed(s)
        a2 = random.expovariate(lmbda)
        b2 = nprandom.choice(choices)
        c2 = random.random()
        self.assertEqual(a1, a2)
        self.assertEqual(b1, b2)
        self.assertEqual(c1, c2)

    def test_randomchoice(self):
        ciw.seed(1)
        array = [1, 2, 3, 4, 5, 6, 7, 8]
        probs = [0.4, 0.2, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05]
        choices = [ciw.random_choice(array, probs) for _ in range(100)]
        choice_counts = Counter(choices)
        self.assertEqual(choice_counts, {1:40, 2:21, 3:13, 4:7, 5:3, 6:6, 7:6, 8:4})

        ciw.seed(2)
        array = ['A', 'B', 'C', 'Ch', 'D', 'Dd', 'E', 'F', 'Ff', 'G', 'Ng', 'H']
        probs = [0.0, 0.1, 0.0, 0.3, 0.0, 0.2, 0.0, 0.1, 0.1, 0.0, 0.2, 0.0]
        choices = [ciw.random_choice(array, probs) for _ in range(300)]
        choice_counts = Counter(choices)
        self.assertEqual(choice_counts, {'B':30, 'Ch':87, 'Dd':70, 'F':28, 'Ff':31, 'Ng':54})

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
        self.assertEqual(choice_counts, {111: 196, 222: 193, 333: 213, 444: 198})

