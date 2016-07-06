.. _baulking-functions:

========
Baulking
========

Ciw allows customer's to baulk (not join the queue) upon arrival, according to a baulking function. This function takes in a parameter :code:`n`, the number of individuals at the node, and returns a probability of baulking.

For example, say we have an M/M/1 system where customers never baulk if there are less than 3 customers in the system, probability 0.5 of baulking if there are between 3 and 6 customers in the system, and always baulk if there are more than 6 customers in the system. We can define the following baulking function::

    def my_baulking_function(n):
        if n < 3:
           return 0.0
        if n < 7:
           return 0.5
        return 1.0

In the parameter's dictionary we tell Ciw which node and customer class this function applies to with the :code:`Baulking_functions` key::

    'Baulking_functions': {'Class 0': [my_baulking_function]}

or if there is only one customer class::

    'Baulking_functions': [my_baulking_function]

Note that baulking works and behaves differently to simply setting a queue capacity. Filling a queue's capacity results in arriving customers begin *rejected* (and recorded in the :code:`rejection_dict`), and transitioning customers to be blocked. Baulking on the other hand does not effect transitioning customers, and customer who have baulked are recorded in the :code:`baulked_dict`. This means that if you set a deterministic baulking threshold of 5, but do not set a queue capacity, then the number of individuals at that node may exceed 5, due to customers transitioning from other nodes ignoring the baulking threshold.

The :code:`baulked_dict` is an attribute of the Simulation object::

    >>> Q.baulked_dict # doctest:+SKIP