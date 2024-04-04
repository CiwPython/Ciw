from typing import List

from ciw.individual import Individual
from ciw.auxiliary import random_choice


def FIFO(individuals: List[Individual], t: float) -> Individual:
    """
    FIFO: First In, First Out (FIFO)

    Returns the individual at the head of the queue.

    Parameters:
    - individuals (List[Individual]): List of individuals in the queue.
    - t (float): The current simulation time

    Returns:
    - Individual: The individual at the head of the queue.
    """
    return individuals[0]


def SIRO(individuals: List[Individual], t: float) -> Individual:
    """
    SIRO: Service In Random Order (SIRO)

    Returns a random individual from the queue.

    Parameters:
    - individuals (List[Individual]): List of individuals in the queue.
    - t (float): The current simulation time

    Returns:
    - Individual: A randomly selected individual from the queue.
    """
    return random_choice(individuals)


def LIFO(individuals: List[Individual], t: float) -> Individual:
    """
    LIFO: Last In, First Out (LIFO)

    Returns the individual who joined the queue most recently.

    Parameters:
    - individuals (List[Individual]): List of individuals in the queue.
    - t (float): The current simulation time

    Returns:
    - Individual: The individual who joined the queue most recently.
    """
    return individuals[-1]
