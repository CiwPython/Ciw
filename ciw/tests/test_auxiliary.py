import unittest
import ciw
import random
import numpy.random as nprandom
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