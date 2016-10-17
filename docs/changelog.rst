.. _changes:

Change Log
==========

v0.2.6 (2016-10-17)
-------------------
Add AUTHORS.rst.
Add progress bar option.

v0.2.5 (2016-10-06)
-------------------
Fix bug that didn't include .rst files in MANIFEST.in.

v0.2.4 (2016-09-27)
-------------------
Fixed bug in which priority classes and dynamic classes didn't work together.
New feature: preemptive interruptions for server schedules.

v0.2.3 (2016-07-27)
-------------------
Ability to set seed. More docs. Fixes to tests.

v0.2.2 (2016-07-06)
-------------------
Baulking implemented, and minor fixes to order of unblocking.

v0.2.1 (2016-06-29)
-------------------
Priority classes implemented.

v0.2.0 (2016-06-20)
-------------------
Python 3.4 and 3.5 compatible along with 2.7.
Data records now kept in list.

v0.1.1 (2016-06-06)
-------------------
Ability to incorporate behaviour nodes.
Data records are now named tuples.

v0.1.0 (2016-04-25)
-------------------
Re-factor inputs.
Simulation takes in a Network object.
Helper functions to import yml and dictionary to a Network object.
Simulation object takes optional arguments: deadlock_detector, exact, tracker.
simulate_until_max_time() takes argument max_simulation_time.

v0.0.6 (2016-04-04)
-------------------
Exactness implemented.
Restructure some features e.g. times_to_deadlock.
Custom simulation names.

v0.0.5 (2016-03-18)
-------------------
State space tracker plug-and-playable.
Add rejection dictionary.

v0.0.4 (2016-02-20)
-------------------
Empirical and UserDefined distributions added.
Tidy ups.

v0.0.3 (2016-02-09)
-------------------
Arrival distributions.
MMC options removed.
Fix server schedule bugs.

v0.0.2 (2016-01-06)
-------------------
Some kwargs optional.
Hypothesis tests.
Minor enhancements.

v0.0.1 (2015-12-14)
-------------------
Initial release.

v0.0.1dev (2015-12-14)
----------------------
Initial release (dev).
