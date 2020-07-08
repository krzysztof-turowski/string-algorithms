import itertools
import os
import unittest

from compression import burrows_wheeler
from string_indexing import suffix_array

class TestBurrowsWheeler(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_burrows_wheeler(self, t, n, reference):
    self.assertEqual(burrows_wheeler.transform_from_suffix_array(
        suffix_array.naive(t, n), t, n), reference)

  def check_inverse_burrows_wheeler(self, bwt, n, reference):
    self.assertEqual(burrows_wheeler.inverse_transform_naive(bwt, n), reference)

  def test_burrows_wheeler(self):
    self.check_burrows_wheeler('#abaaba', 6, '#abba$aa')
    self.check_burrows_wheeler('#banana', 6, '#annb$aa')

  def test_inverse_burrows_wheeler(self):
    self.check_inverse_burrows_wheeler('#abba$aa', 6, '#abaaba')
    self.check_inverse_burrows_wheeler('#annb$aa', 6, '#banana')
