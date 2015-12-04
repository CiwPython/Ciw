.. _dynamic-classes:

========================
Dynamic Customer Classes
========================

ASQ allows customers to probabilistically change their class after service. That is after service at node `k` a customer of class `i` will become class `j` with probability `P(J=j | I=i, K=k)`. These probabilities are input into the system through the :code:`Class_change_matrices`.

Below is an example of a class change matrix for a given node:

+-----------------+
| Node 1          |
+=====+=====+=====+
| 0.3 | 0.4 | 0.3 |
+-----+-----+-----+
| 0.1 | 0.9 | 0.0 |
+-----+-----+-----+
| 0.5 | 0.1 | 0.4 |
+-----+-----+-----+

+-----------------+
| Node 2          |
+=====+=====+=====+
| 1.0 | 0.0 | 0.0 |
+-----+-----+-----+
| 0.4 | 0.5 | 0.1 |
+-----+-----+-----+
| 0.2 | 0.2 | 0.6 |
+-----+-----+-----+

In this example a customer of class 0 finishing service at node 1 will become class 0 again with probability 0.3, will become class 1 with probability 0.4, and will become class 2 with probability 0.3. A different matrix is given for customers finishing service at node 2.

This is input into the simulation model by including the following code in the parameters file::

    Class_change_matrices:
      Node 0:
      - - 0.7
        - 0.3
      - - 0.2
        - 0.8
      Node 1:
      - - 1.0
        - 0.0
      - - 0.0
        - 1.0

Omitting this code will simply assume that customers cannot change class after service.