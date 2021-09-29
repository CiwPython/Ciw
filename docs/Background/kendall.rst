.. _kendall-notation:

==================
Kendall's Notation
==================

Kendall's notation is used as shorthand to denote single node queueing systems [WS09]_.

A queue is characterised by:

.. math::

    A/B/C/X/Y/Z

where:

+ :math:`A` denotes the distribution of inter-arrival times
+ :math:`B` denotes the distribution of service times
+ :math:`C` denotes the number of servers
+ :math:`X` denotes the queueing capacity
+ :math:`Y` denotes the size of the population of customers
+ :math:`Z` denotes the queueing discipline

For the parameters :math:`A` and :math:`B`, a number of shorthand notation is available. For example:

+ :math:`M`: Markovian or Exponential distribution
+ :math:`E`: Erlang distribution (a special case of the Gamma distribution)
+ :math:`C_k`: Coxian distribution of order :math:`k`
+ :math:`D`: Deterministic distribution
+ :math:`G` / :math:`GI`: General / General independent distribution

The parameters :math:`X`, :math:`Y` and :math:`Z` are optional, and are assumed to be :math:`\infty`, :math:`\infty`, and First In First Out (FIFO) respectively.
Other options for the queueing schedule :math:`Z` may be SIRO (Service In Random Order), LIFO (Last In First Out), and PS (Processor Sharing).

Some examples:

+ :math:`M/M/1`:
   + Exponential inter-arrival times
   + Exponential service times
   + 1 server
   + Infinite queueing capacity
   + Infinite population
   + First in first out

+ :math:`M/D/\infty/\infty/1000`:
   + Exponential inter-arrival times
   + Deterministic service times
   + Infinite servers
   + Infinite queueing capacity
   + Population of 1000 customers
   + First in first out

+ :math:`G/G/1/\infty/\infty/\text{SIRO}`:
   + General distribution for inter-arrival times
   + General distribution for service times
   + 1 server
   + Infinite queueing capacity
   + Infinite population
   + Service in random order

+ :math:`M/M/4/5`:
   + Exponential inter-arrival times
   + Exponential service times
   + 4 servers
   + Queueing capacity of 5
   + Infinite population
   + First in first out

