A Package for Simulating a Queueing network
===========================================

A simulation of a queueing network.
Consists the following programs: simulation.py, experiment.py, run_simulation.py, analyse.py


simulation.py
-------------

Contains all classes and methods needed to simulate a queueing network


run_simulation.py
-----------------

Runs the simulation once until max_time, writes results to data.csv file.
Run this file with the docopt argument <dirname>, which will read in a parameters.yml file from that directory.


experiment.py
-------------

Runs an the simulation 'Number of Iterations' times for every parameter change.
Run this file with the docopt argument <dirname>, which will read in a parameters.yml file and a config.yml file from that directory.


analyse.py
----------

Analyses the results.
Run this file after run_simulation.py with docopt argument <dirname>, which will read in a parameters.yml and data.csv file from that direftory.