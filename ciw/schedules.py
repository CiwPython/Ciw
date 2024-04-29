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
    shift_end_dates : List[float]
        List of shift end dates.
    numbers_of_servers : List[int]
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
    def __init__(self, numbers_of_servers: List[int], shift_end_dates: List[float], preemption: Union[bool, str] = False, offset: float = 0.0) -> NoReturn:
        """
        Initializes the instance of the Schedule object.

        Parameters
        ----------
        numbers_of_servers : List[int]
            A list containing the number of servers working at each shift
        shift_end_dates : List[float]
            A list containing the end dates of each shift.
        preemption : Union[bool, str], optional
            Pre-emption option, should be either 'resume', 'restart',
            'resample', or False.
            Default is False.
        """
        if preemption not in [False, 'resume', 'restart', 'resample', 'reroute']:
            raise ValueError("Pre-emption options should be either 'resume', 'restart', 'resample', 'reroute', or False.")
        if not isinstance(offset, float):
            raise ValueError("Offset should be a positive float.")
        if offset < 0.0:
            raise ValueError("Offset should be a positive float.")
        self.schedule_type = 'schedule'
        self.shift_end_dates = shift_end_dates
        self.numbers_of_servers = numbers_of_servers
        self.preemption = preemption
        self.cyclelength = self.shift_end_dates[-1]
        self.offset = offset

    def initialise(self) -> NoReturn:
        """
        Initializes the generator object at the beginning of a simulation.
        """
        self.c = 0
        self.next_shift_change_date = self.offset
        self.next_c = self.numbers_of_servers[0]
        self.schedule_generator = self.get_schedule_generator(self.shift_end_dates, self.numbers_of_servers, self.offset)

    def get_schedule_generator(self, boundaries:List[float], values:List[int], offset:float) -> Generator[Tuple[float, int], None, None]:
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
            date = offset + boundaries[index % num_boundaries] + ((index) // num_boundaries * self.cyclelength)
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
    def __init__(self, slots, slot_sizes, capacitated=False, preemption=False, offset=0.0):
        """
        Initialises the instance of the Slotted Schedule object
        """
        if not capacitated:
            if preemption is not False:
                raise ValueError("Pre-emption options not availale for non-capacitated slots.")
        if preemption not in [False, 'resume', 'restart', 'resample']:
            raise ValueError("Pre-emption options should be either 'resume', 'restart', 'resample', or False.")
        if not isinstance(offset, float):
            raise ValueError("Offset should be a positive float.")
        if offset < 0.0:
            raise ValueError("Offset should be a positive float.")
        self.schedule_type = 'slotted'
        self.offset = offset
        self.slots = slots
        self.slot_sizes = slot_sizes
        self.next_slot_sizes = [self.slot_sizes[-1]] + self.slot_sizes[:-1]
        self.capacitated = capacitated
        self.preemption = preemption
        self.cyclelength = self.slots[-1]
        self.c = 0

    def initialise(self):
        """
        Initialises the generator object at the beginning of a simulation
        """
        self.schedule_generator = self.get_schedule_generator(self.slots, self.next_slot_sizes, self.offset)
        self.get_next_slot()

    def get_next_slot(self):
        """
        Updates the next slot time and size from the generator
        """
        date, size = next(self.schedule_generator)
        self.next_slot_date = date
        self.slot_size = size
