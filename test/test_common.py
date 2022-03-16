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

  @run_large
  def test_all_weak_boyer_moore_shift(self):
    M, A = 10, ['a', 'b', 'c']
    for m in range(2, M + 1):
      for w in itertools.product(A, repeat = m):
        w = '#' + ''.join(w)
        reference = suffix.weak_boyer_moore_shift_brute_force(w, m)
        result = suffix.weak_boyer_moore_shift(w, m)
        self.assertEqual(result, reference)

  @run_large
  def test_all_boyer_moore_shift(self):
    M, A = 10, ['a', 'b', 'c']
    for m in range(2, M + 1):
      for w in itertools.product(A, repeat = m):
        w = '#' + ''.join(w)
        reference = suffix.boyer_moore_shift_brute_force(w, m)
        result = suffix.boyer_moore_shift(w, m)
        self.assertEqual(result, reference)
