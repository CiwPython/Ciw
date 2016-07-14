from random import seed as rseed
from numpy import random

def seed(z):
	rseed(z)
	random.seed(z)