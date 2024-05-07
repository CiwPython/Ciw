.. _ciw-mechanisms:

=========================
Notes on Ciw's Mechanisms
=========================

General
~~~~~~~

Ciw uses the *event scheduling* approach [SR14]_ , similar to the three phase approach.
In the event scheduling approach, three types of event take place: **A Events** move the clock forward, **B Events** are prescheduled events, and **C Events** are events that arise because a **B Event** has happened.

Here **A-events** correspond to moving the clock forward to the next **B-event**.
**B-events** correspond to either an external arrival, a customer finishing service, or a server shift change.
**C-events** correspond to a customer starting service, customer being released from a node, and being blocked or unblocked.

In event scheduling the following process occurs:

1. Initialise the simulation
2. **A Phase**: move the clock to the next scheduled event
3. Take a **B Event** scheduled for now, carry out the event
4. Carry out all **C Events** that arose due to the event carried out in (3.)
5. Repeat (3.) - (4.) until all **B Event** scheduled for that date have been carried out
6. Repeat (2.) - (5.) until a terminating criteria has been satisfied



.. _simultaneous_events:

Simultaneous Events
~~~~~~~~~~~~~~~~~~~

In discrete event simulation, simultaneous event are inevitable.
That is two or more events that are scheduled to happen at the same time.
However due to the nature of discrete event simulation, these event cannot be carried out computationally at the same time, and the order at which these events are computed can greatly effect their eventual outcome.
For example, if two customers are scheduled to arrive at an empty :ref:`M/M/1 <kendall-notation>` queue at the same date: which one should begin service and which one should wait?

In Ciw, to prevent any bias, whenever more than one event is scheduled to happen simultaneously, the next event to be computed is uniformly randomly selected from the list of events to be undertaken.


