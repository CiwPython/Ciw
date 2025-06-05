"""
Tests the version number
"""
from ciw import __version__
import unittest


class TestVersion(unittest.TestCase):
    def test_version(self):
        self.assertIsInstance(__version__, str)
