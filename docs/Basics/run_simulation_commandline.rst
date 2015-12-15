.. _command-line-tool:

=====================
The Command Line Tool
=====================

This page will describe how to run the experiment via the command line.
Set up a new folder alongside Ciw that will contain your parameters file::

    .
    ├── my_simulation_instance
    │   └── parameters.yml
    │
    ├── Ciw

The parameters.yml file is a yaml file containing all the parameters that describe the queueing network you would like to simulate. See :ref:`parameters-file` for how to set up this file.

To run the simulation go to the directory which contains both :code:`Ciw` and :code:`my_simultion_instance`.
Then run the following command::

    $ python Ciw/scripts/run_simulation.py my_simulation_instance/

This will create a :code:`data.csv`, positioned here::

    .
    ├── my_simulation_instance
    │   └── parameters.yml
    │   └── data.csv
    ├── Ciw

Please see :ref:`output-file` for an explanation of the data contained here.