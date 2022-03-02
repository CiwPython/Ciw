============
Contributing
============

Contributions from anyone are awesome! This may include opening `issues <https://github.com/CiwPython/Ciw/issues>`_, communicating ideas for new features, letting us know about use cases of the library, and code contributions. We would love to recieve your pull requests. Here's a handy guide:

Fork, then clone the repo::

    git clone git@github.com:your-username/Ciw.git

Install the testing dependencies::

    python -m pip install -r test_requirements.txt

Install a development version of the library::

    python -m pip install -r requirements.txt
    python setup.py develop

Make sure the tests pass (Ciw uses unit & doc testing)::

    python -m unittest discover ciw
    python doctests.py

We encourage the use of coverage, ensuring all aspects of the code are tested::

    coverage run --source=ciw -m unittest discover ciw.tests
    coverage report -m

Add tests for your change. Make your change and make the tests pass.

Please update the documentation too, and ensure doctests pass.
To build the documentation::

    cd docs
    python -m pip install -r requirements.txt
    make html

Push to your fork and submit a pull request!

Some ideas of where to begin:

- Take a look through our `issues <https://github.com/CiwPython/Ciw/issues>`_.
- Open new issues!
- Bug reporting & fixes.
- Code tidying & performance improvements.
- Improvements to the `documentation <http://ciw.readthedocs.io>`_.
- New features.

We look forward to your contributions!
