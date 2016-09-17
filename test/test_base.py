import unittest
import sys

# Include upper level files for testing
sys.path.append("..")

# Try to use the correct version of mock
try:
    from unittest.mock import *
except ImportError:
    from mock import *

# Deal with v2 and v3 differences in int types
if sys.version_info < (3,):
    integer_types = (int, long,)
else:
    integer_types = (int,)

# Root case for all test cases
class BaseCase(unittest.TestCase):
    """Root case for all test cases"""
    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(__class__)