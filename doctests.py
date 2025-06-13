"""Test hook(s) for Doctests in reStructuredText (.rst) Files."""

import doctest
import os
import unittest
import sys
from typing import Any


def load_tests(loader: unittest.TestLoader, tests: unittest.TestSuite, ignorex: Any) -> unittest.TestSuite:
    """
    Discover and add all reStructuredText (.rst) doctest files within the current directory tree to the test suite.

    Parameters
    ----------
    loader : unittest.TestLoader
        The test loader instance used to load the tests.
    tests : unittest.TestSuite
        The existing test suite to which doctest suites will be added.
    ignorex : Any
        A placeholder parameter (typically unused) required by the unittest framework.

    Returns
    -------
    unittest.TestSuite
        The updated test suite including all discovered .rst doctest files.

    Notes
    -----
    This function is used by the unittest framework to discover and include additional doctests
    in the test suite during test discovery.

    Examples
    --------
    When placed in a test module, unittest will automatically call `load_tests` if it exists.

    >>> import unittest
    >>> suite = unittest.TestSuite()
    >>> loader = unittest.TestLoader()
    >>> load_tests(loader, suite, None)  # doctest: +ELLIPSIS
    <unittest.suite.TestSuite tests=[...]
    """
    for root, dirs, files in os.walk("."):
        for f in files:
            if f.endswith(".rst"):
                tests.addTests(
                    doctest.DocFileSuite(
                        os.path.join(root, f),
                        optionflags=doctest.ELLIPSIS
                    )
                )
    return tests


if __name__ == "__main__":
    if sys.version_info >= (3, 6):
        unittest.main()

