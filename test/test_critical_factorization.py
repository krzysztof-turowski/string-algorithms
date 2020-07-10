import itertools
import os
import unittest

from generator import rand
from lyndon import critical_factorization

class TestCriticalFactorization(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_critical_factorization(self, t, n, reference):
    self.assertIn(critical_factorization.constant_space(t, n), reference)

  def test_critical_factorization(self):
    self.check_critical_factorization('#aababb', 6, [(5, 1)])
    self.check_critical_factorization('#GCAGAGAG', 8, [(3, 2)])
    self.check_critical_factorization('#ababbaba', 8, [(4, 5)])
    self.check_critical_factorization('#abaabaa', 7, [(3, 3)])

  @run_large
  def test_random_critical_factorization(self):
    T, n, A = 100, 300, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      reference = critical_factorization.naive_all(t, n)
      self.check_critical_factorization(t, n, reference)

  @run_large
  def test_all_critical_factorization(self):
    N, A = 14, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        reference = critical_factorization.naive_all(t, n)
        self.check_critical_factorization(t, n, reference)
