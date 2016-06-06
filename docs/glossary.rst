.. _glossary:

Glossary
========

.. glossary::

   arrival
      The event in which a customer enters a node.

   arrival distribution
      The distribution that a node's inter-arrival times are drawn from.

   blocking
      Blocking occurs when a customer finishes service and attempts to transition to their destination node, however that node's queueing capacity is full. In this case a blockage occurs where the customer remains at the original node, still holding a server, until space becomes free at the destination node. During this blockage time, the held server is not free to serve any other customers.

   closed
      A queueing network is described as closed is customers cannot arrive from the outside nor completely leave the system.

   customer
      The entities that are being simulated as they wait, spend time in service, and flow through the system. (Interchangeable with `individual`.)

   cycle length
      The length of a cycle of a `work schedule`.

   deadlock
      A state of mutual blocking whereby a subset of customers may never move due to circular blockages.

   external arrival
      An external arrival is an arrival from outside the network. That is all arrivals to nodes where customers have not transitioned from another node.

   individual
      Interchangeable with `customer`.

   node
      A node contains a queue of waiting customers, and a service centre of servers.

   open
      A queueing network is described as open is customers can arrive from the outside and completely leave the system.

   queue
      The part of the node in which customers wait. Waiting follows a first-in-first-out (FIFO) discipline.

   queueing network
      A set of nodes, connected in a network by a transition matrix.

   queueing capacity
      A node's queueing capacity is the maximum number of customers allowed to wait at the node at any time.

   restricted
      A queueing network is described as restricted if there are nodes with limited queueing capacity, and blockages may occur.

   server
      A resource that a customer holds for their period of time in service. The server is also held during blockage times.

   server schedule
      Interchangeable with `work schedule`.

   service
      The period of time which the customer spends with a server. This is the activity which customers wait to begin.

   service centre
      The part of a node in which customers are served. This can contain multiple parallel servers. (Interchangeable with `service station`).

   service distribution
      The distribution that a customer's service times are drawn from.

   service station
      Interchangeable with `service centre`.

   traffic intensity
      The traffic intensity is a measure of how busy the system becomes. For a given node it is defined as the ratio of the mean service time of the mean inter arrival time.

   transition matrix
      A matrix of transition probabilities. The entry in row `i` of column `j`, :math:`r_{ij}`, is the probability of transitioning to node `j` after service at node `i`.

   warm-up time
      A period of time at the beginning of a simulation where the data records do not count towards any analysis. This is due to the bias of beginning the simulation from an empty system. Results are only analysed after the system has reached some form of steady-state.

   work schedule
      A schedule of how many servers are present at certain time periods for a given node. Work schedules are cyclic, and so once the `cycle length` has been reached the schedule begins again.