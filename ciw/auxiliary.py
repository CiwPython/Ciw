from random import seed as rseed
from numpy import random

def seed(z):
	rseed(z)
	random.seed(z)

def random_choice(array, probs=None):
	"""
	This function takes in an array of values to make a choice from,
	and an pdf corresponding to those values. It returns a random choice
	from that array, using the probs as weights.
	"""
	if probs == None:
		lenarr = len(array)
		probs = [1/lenarr for _ in range(lenarr)]

	rdm_num = random.random()
	i, p = 0, probs[0]
	while rdm_num > p:
		i += 1
		p += probs[i]
	return array[i]