from typing import List, Tuple, Union, Generator, NoReturn

class Schedule:
    """
    A Schedule class for storing information about server schedules and
    generating the next shifts.

    Parameters
    ----------
    schedule : List[Tuple[int, float]]
        A list of tuples representing shifts, where each tuple contains the
        number of servers and the shift end date.
    preemption : Union[bool, str], optional
        Pre-emption option, should be either 'resume', 'restart', 'resample',
        or False. Default is False.

    Attributes
    ----------
    schedule_type : str
        Type of the schedule.
    schedule_dates : List[float]
        List of shift end dates.
    schedule_servers : List[int]
        List of corresponding server numbers.
    preemption : Union[bool, str]
        Pre-emption option.
    cyclelength : float
        Length of the schedule cycle.

    Methods
    -------
    initialise()
        Initializes the generator object at the beginning of a simulation.
    get_schedule_generator(boundaries, values)
        A generator that yields the next time and number of servers according
        to a given schedule.
    get_next_shift()
        Updates the next shifts from the generator.
    """
    def __init__(self, schedule: List[Tuple[int, float]], preemption: Union[bool, str] = False) -> NoReturn:
        """
        Initializes the instance of the Schedule object.

        Parameters
        ----------
        schedule : List[Tuple[int, float]]
            A list of tuples representing shifts, where each tuple contains
            the number of servers and the shift date.
        preemption : Union[bool, str], optional
            Pre-emption option, should be either 'resume', 'restart',
            'resample', or False.
            Default is False.
        """
        if preemption not in [False, 'resume', 'restart', 'resample']:
            raise ValueError("Pre-emption options should be either 'resume', 'restart', 'resample', or False.")
        self.schedule_type = 'schedule'
        self.schedule_dates = [shift[1] for shift in schedule]
        self.schedule_servers = [shift[0] for shift in schedule]
        self.preemption = preemption
        self.cyclelength = self.schedule_dates[-1]

    def initialise(self) -> NoReturn:
        """
        Initializes the generator object at the beginning of a simulation.
        """
        self.next_c = self.schedule_servers[0]
        self.schedule_generator = self.get_schedule_generator(self.schedule_dates, self.schedule_servers)
        self.get_next_shift()

    def get_schedule_generator(self, boundaries: List[float], values:List[int]) -> Generator[Tuple[float, int], None, None]:
        """
        A generator that yields the next time and number of servers according
        to a given schedule.

        Parameters
        ----------
        boundaries : List[float]
            List of shift boundaries.
        values : List[int]
            List of corresponding server numbers.

        Yields
        ------
        Tuple[float, int]
            A tuple representing the next shift date and the number of servers.
        """
        num_boundaries = len(boundaries)
        index = 0
        date = 0
        while True:
            date = boundaries[index % num_boundaries] + ((index) // num_boundaries * self.cyclelength)
            index += 1
            yield date, values[index % num_boundaries]

    def get_next_shift(self) -> NoReturn:
        """
        Updates the next shifts from the generator.
        """
        self.c = self.next_c
        date, c = next(self.schedule_generator)
        self.next_shift_change_date = date
        self.next_c = c


class Slotted(Schedule):
    def __init__(self, slots, slot_sizes, capacitated=False, preemption=False):
        """
        Initialises the instance of the Slotted Schedule object
        """
        if not capacitated:
            if preemption is not False:
                raise ValueError("Pre-emption options not availale for non-capacitated slots.")
        if preemption not in [False, 'resume', 'restart', 'resample']:
            raise ValueError("Pre-emption options should be either 'resume', 'restart', 'resample', or False.")
        self.schedule_type = 'slotted'
        self.slots = slots
        self.slot_sizes = slot_sizes
        self.capacitated = capacitated
        self.preemption = preemption
        self.cyclelength = self.slots[-1]
        self.c = 0


    def initialise(self):
        """
        Initialises the generator object at the beginning of a simulation
        """
        self.schedule_generator = self.get_schedule_generator(self.slots, [self.slot_sizes[-1]] + self.slot_sizes[:-1])
        self.get_next_slot()

    def get_next_slot(self):
        """
        Updates the next slot time and size from the generator
        """
        date, size = next(self.schedule_generator)
        self.next_slot_date = date
        self.slot_size = size
