import itertools
import os
import unittest

from common import prefix, suffix

class TestCommon(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def test_overlap(self):
    self.assertEqual(prefix.get_overlap('#aba','#bab'), 2)
    self.assertEqual(prefix.get_overlap('#abab','#bab'), 3)
    self.assertEqual(prefix.get_overlap('#abb','#ab'), 0)
    self.assertEqual(prefix.get_overlap('#aa','#aa'), 1)
    self.assertEqual(prefix.get_overlap('#aab','#aab'), 0)
    self.assertEqual(prefix.get_overlap('#undergrounder', '#undergrounder'), 5)
