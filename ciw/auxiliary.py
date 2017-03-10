import random

def seed(z):
	"""
	Sets all seeds used to generate random number streams.
	Currently conrains:
		- random library
	Previously contained:
		- numpy
	"""
	random.seed(z)

def random_choice(array, probs=None):
	"""
	This function takes in an array of values to make a choice from,
	and an pdf corresponding to those values. It returns a random choice
	from that array, using the probs as weights.
	"""
	# If no pdf provided, assume uniform dist:
	if probs == None:
		lenarr = len(array)
		probs = [1.0/lenarr for _ in range(lenarr)]

	# A common case, guaranteed to reach the Exit node;
	# No need to sample for this:
	if (set(probs[:-1]) == set([0.0])) and (probs[-1] == 1.0):
		return array[-1]

	# Sample a random value from using pdf
	rdm_num = random.random()
	i, p = 0, probs[0]
	while rdm_num > p:
		i += 1
		p += probs[i]
	return array[i]