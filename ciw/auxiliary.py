import random

def seed(z):
	"""
	Sets all seeds used to generate random number streams.
	Currently contains:
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
		index = int(random.random() * len(array))
		return array[index]

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

def truncated_normal(mean, sd):
	"""
	Sample from a Normal distribution, with mean and standard
	deviation (sd). This truncates the distribution at 0 (lower bound
	of 0). If samples less than 0 are sampled, they are resampled
    until a positive value is sampled.
	"""
	sample = random.normalvariate(mean, sd)
	while sample <= 0.0:
		sample = random.normalvariate(mean, sd)
	return sample

def flatten_list(list_of_lists):
	flat = []
	for a_list in list_of_lists:
		flat += a_list
	return flat

def no_routing(ind):
	"""
	Process-based routing fucntion that sends the customer straight
	to exit node. It is a placeholder for when NoArrivals is used. 
	"""
	return []