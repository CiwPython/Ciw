class Schedule:
    """
    A Schedule class, for storing information about server schedules and
    generating the next shifts.
    """
    def __init__(self, schedule, preemption=False):
        """
        Initialises the instance of the Schedule object
        """
        self.schedule_type = 'schedule'
        self.schedule_dates = [shift[1] for shift in schedule]
        self.schedule_servers = [shift[0] for shift in schedule]
        self.preemption = preemption
        self.cyclelength = self.schedule_dates[-1]

    def initialise(self):
        """
        Initialises the generator object at the beginning of a simulation
        """
        self.next_c = self.schedule_servers[0]
        self.schedule_generator = self.get_schedule_generator(self.schedule_dates, self.schedule_servers)
        self.get_next_shift()

    def get_schedule_generator(self, boundaries, values):
        """
        A generator that yields the next time and number of servers according to a given schedule.
        """
        num_boundaries = len(boundaries)
        index = 0
        date = 0
        while True:
            date = boundaries[index % num_boundaries] + ((index) // num_boundaries * self.cyclelength)
            index += 1
            yield date, values[index % num_boundaries]

    def get_next_shift(self):
        """
        Updates the next shifts from the generator
        """
        self.c = self.next_c
        date, c = next(self.schedule_generator)
        self.next_shift_change_date = date
        self.next_c = c


# class Slotted(Schedule):
#     def __init__(self, slots, slot_sizes):
#         self.schedule_type = 'slotted'
#         self.slots = slots
#         self.slot_sizes = slot_sizes