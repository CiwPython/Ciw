History
-------

+ **v2.3.4 (2022-12-07)**
    + PoissonIntervals distribution now allows rates of zero

+ **v2.3.2 (2022-10-07)**
    + Add PoissonIntervals distribution
    + Add numpy random generator, ciw.seed now also creates new random generator
    + Documentation on parallelising trials
    + Remove support for Python 3.6

+ **v2.3.1 (2022-07-25)**
    + Fixes bug where blocked customers were candidates for `finish_service` when more than one customer finishes service simultaneously
    + Correctly writes csv's in Windows
    + Support for Python 3.9 by updating tqdm requirement

+ **v2.3.0 (2022-05-10)**
    + Reneging customers implemented
    + Customer class changes while waiting implemented
    + Preemptive interruption options implemented
    + New record_type field added to DataRecords

+ **v2.2.4 (2022-03-02)**
    + Improve docs on pausing simulations and server priorities
    + Record server ID in the DataRecords
    + Move CI to GitHub Actions

+ **v2.2.3 (2022-01-27)**
    + Server priority functions implemented.

+ **v2.2.2 (2021-12-17)**
    + State trackers now take objects not indices
    + Servers are attached to individuals before sampling service times
    + Docs on sever-dependant distributions
    + Docs on DES+SD hybrid simulations

+ **v2.2.1 (2021-11-04)**
    + PhaseType distributions implemented
    + Classes for specific PhaseType distributions: Erlang, HyperExponential, HyperErlang, and Coxian

+ **v2.2.0 (2021-07-22)**
    + Processor sharing implemented (limited and capacitated)
    + Ability to use a different node_class per node of the network
    + State tracking now works with simulate_until_max_customers
    + Remove testing on Python 3.5

+ **v2.1.3 (2020-10-06)**
    + Small refactor to Node adding new servers, and to Individuals receiving the Simulation object.
    + Add a library of custom behaviour to docs
    + Support Python 3.8, update hypothesis

+ **v2.1.2 (2020-09-26)**
    + Ability to incorporate customer behaviour Server and Individual classes.

+ **v2.1.1 (2020-05-27)**
    + State Trackers slightly more efficent, they do not record any state changes that result in the same state as before.
    + Add the NodePopulationSubset tracker.
    + Distribution objects can now see the Simulation object, for true state dependent distributions.

+ **v2.1.0 (2020-04-23)**
    + State Trackers now track history
    + State Trackers give state probabilities
    + A number of performance improvements
    + Fix some documentation
    + Test on PyPy3.6 and Python 3.7 too

+ **v2.0.1 (2019-07-17)**
    + setup.py now finds packages to fix pip install bug

+ **v2.0.0 (2019-07-10)**
    + Large refactor:
    + Drop support for Python 2.7, Python 3.4.
    + Update networkx and pyyaml requirements.
    + Refactor time so that `Simulation` has `current_time` attribute.
    + Change Transition_matrices keyword to routing.
    + routing can take a process-based routing function.
    + Refactor distributions to be objects: ['Exponential', 0.5] -> ciw.dists.Exponential(0.5).
    + Distribution objects can be manipulated with +, -, * and /.
    + All keywords lower case to conform to Pep8.
    + deadlock_detector keyword takes object, not string.
    + tracker keyword takes object, not string.
    + Add tests and docs to show how objects can be used for state-dependent distributions.
    + All user facing api now takes float('inf') not 'Inf', expect for .yml files.
    + Reference Ciw paper in docs.
    + Add AUTHORS.rst to docs.

+ **v1.1.6 (2018-10-22)**
    + Fixed bug in which preemptively iterrupted individuals remained blocked once service resampled.
    + Fixed bug in which interrupted individuals not removed from interrupted list when restarting service.
    + Some performance improvements.
    + Improve deadlock detection to check for knots less often.


+ **v1.1.5 (2018-01-11)**
    + Fixed bug calculating the utilisation of servers.

+ **v1.1.4 (2017-12-12)**
    + Time dependent batching distributions
    + Hard pin requirements versions

+ **v1.1.3 (2017-08-18)**
    + Replace DataRecord object with namedtuple.
    + Number of minor tweaks for speed improvements.

+ **v1.1.2 (2017-07-05)**
    + Batch arrivals.

+ **v1.1.1 (2017-06-23)**
    + Server utilisation & overtime.
    + Small fixes to docs.
    + Testing on Python 3.6.

+ **v1.1.0 (2017-04-26)**
    + Replace kwargs with actual keyword arguments in ciw.create_network.
    + Refactor server schedule inputs (schedules placed inside Number_of_servers instead of as their own keyword).

+ **v1.0.0 (2017-04-04)**
    + ciw.create_network takes in kwargs, not dictionary.
    + Add Sequential distribution.
    + Add truncated Normal distribution.
    + Refactor inputs for custom PDF.
    + Refactor inputs for server schedules.
    + Transition matrix now optional for 1 node networks.
    + Overhaul of documentation.
    + Add CONTRIBUTING.rst.
    + Slight improvement of ciw.random_choice.

+ **v0.2.11 (2017-03-13)**
    + Add ability to simulate until max number of customers have passed arrived/been accepted/passed through the system.

+ **v0.2.10 (2017-03-10)**
    + Performance improvements.
    + Drop dependency on numpy.

+ **v0.2.9 (2017-02-24)**
    + Allow zero servers.

+ **v0.2.8 (2016-11-10)**
    + Add option for time dependent distributions.

+ **v0.2.7 (2016-10-26)**
    + Run tests on Appveyor.
    + Check docs build and pip installable on Travis.
    + Remove hypothesis cache.

+ **v0.2.6 (2016-10-17)**
    + Add AUTHORS.rst.
    + Add progress bar option.

+ **v0.2.5 (2016-10-06)**
    + Fix bug that didn't include .rst files in MANIFEST.in.

+ **v0.2.4 (2016-09-27)**
    + Fixed bug in which priority classes and dynamic classes didn't work together.
    + New feature: preemptive interruptions for server schedules.

+ **v0.2.3 (2016-07-27)**
    + Ability to set seed. More docs. Fixes to tests.

+ **v0.2.2 (2016-07-06)**
    + Baulking implemented, and minor fixes to order of unblocking.

+ **v0.2.1 (2016-06-29)**
    + Priority classes implemented.

+ **v0.2.0 (2016-06-20)**
    + Python 3.4 and 3.5 compatible along with 2.7.
    + Data records now kept in list.

+ **v0.1.1 (2016-06-06)**
    + Ability to incorporate behaviour nodes.
    + Data records are now named tuples.

+ **v0.1.0 (2016-04-25)**
    + Re-factor inputs.
    + Simulation takes in a Network object.
    + Helper functions to import yml and dictionary to a Network object.
    + Simulation object takes optional arguments: deadlock_detector, exact, tracker.
    + simulate_until_max_time() takes argument max_simulation_time.

+ **v0.0.6 (2016-04-04)**
    + Exactness implemented.
    + Restructure some features e.g. times_to_deadlock.
    + Custom simulation names.

+ **v0.0.5 (2016-03-18)**
    + State space tracker plug-and-playable.
    + Add rejection dictionary.

+ **v0.0.4 (2016-02-20)**
    + Empirical and UserDefined distributions added.
    + Tidy ups.

+ **v0.0.3 (2016-02-09)**
    + Arrival distributions.
    + MMC options removed.
    + Fix server schedule bugs.

+ **v0.0.2 (2016-01-06)**
    + Some kwargs optional.
    + Hypothesis tests.
    + Minor enhancements.

+ **v0.0.1 (2015-12-14)**
    + Initial release.

+ **v0.0.1dev (2015-12-14)**
    + Initial release (dev).
