from ciw.auxiliary import random_choice


def FIFO(individuals):
    """
    FIFO: First in first out / First come first served
    Returns the individual at the head of the queue
    """
    return individuals[0]


def SIRO(individuals):
    """
    SIRO: Service in random order
    Returns a random individual from the queue
    """
    return random_choice(individuals)


def LIFO(individuals):
    """
    LIFO: Last in first out / Last come first served
    Returns the individual who joined the queue most recently
    """
    return individuals[-1]
