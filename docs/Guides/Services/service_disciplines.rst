.. _service-disciplines:

================================
How to Change Service Discipline
================================

Service disciplines determine the order in which customers are served when waiting in the queue. By default, Ciw assumes a First In First Out (FIFO) service, that is, customers are served in the order they arrive in. Ciw does also allow other service disciplines, for example :ref:`priority classes <priority-custs>` can be set where some classes of customer are server before other classes, regardless of their arrival dates. Note also that :ref:`processor sharing <processor-sharing>`, another service discipline, is available in Ciw, but is implemented in a different way.

Ciw allows for different service disciplines to be used at different nodes. These are implemented by using service discipline functions. There are three pre-written functions available for users:

+ **FIFO**: 'First in first out' (or alternatively 'First come first served'). Here the customer who arrived first is served next. To implement this use :code:`ciw.disciplines.FIFO`.
+ **LIFO**: 'Last in first out' (or alternatively 'Last in first served'). Here customer who arrived most recently is served next. This is also sometimes called a 'stack'. To implement this use :code:`ciw.disciplines.LIFO`.
+ **SIRO**: 'Service in random order'. Here the a customer is chosen randomly to be served next. To implement this use :code:`ciw.disciplines.SIRO`.

As an example, say we have a three node network, and we want to use FIFO discipline at node 1, LIFO at node 2, and SIRO at node 3, then we would create a network using the :code:`service_disciplines` keyword:

	>>> import ciw
	>>> N = ciw.create_network(
	...     arrival_distributions=[ciw.dists.Exponential(rate=5),
	...                            ciw.dists.Exponential(rate=5),
	...                            ciw.dists.Exponential(rate=5)],
	...     service_distributions=[ciw.dists.Exponential(rate=10),
	...                            ciw.dists.Exponential(rate=10),
	...                            ciw.dists.Exponential(rate=10)],
	...     service_disciplines=[ciw.disciplines.FIFO,
	...                          ciw.disciplines.LIFO,
	...                          ciw.disciplines.SIRO],
	...     number_of_servers=[1, 1, 1],
	...     routing=[[0.0, 0.5, 0.5],
	...              [0.0, 0.0, 0.5],
	...              [0.0, 0.0, 0.0]]
	... )

**Note:** When using priority classes, service disciplines come into effect *within* a given priority class, but all customers of a higher priority class will be served before any customer of a lower priority service class, whatever service discipline is chosen.



Custom Disciplines
------------------

Other service disciplines can also be implemented by writing a custom service discipline function. These functions take in a list of individuals, and the current time, and returns an individual from that list that represents the next individual to be served. As this is a list of individuals, we can access the individuals' attributes when making the service discipline decision.

For example, say we wish to implement a service discipline that chooses the customers randomly, but with probability proportional to their arrival order, we could write::

    >>> def SIRO_proportional(individuals, t):
    ...     n = len(inds)
    ...     denominator = (n * (n + 1)) / 2
    ...     probs = [(n - i) / denominator for i in range(n)]
    ...     return ciw.random_choice(individuals, probs=probs)


