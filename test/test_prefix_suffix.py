import itertools
import os
import unittest

from common import prefix, suffix
from generator import rand

class TestPrefixSuffixArrays(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_prefix_suffix(self, t, n, reference):
    self.assertEqual(prefix.prefix_suffix_brute_force(t, n), reference)
    self.assertEqual(prefix.prefix_suffix(t, n), reference)
    self.assertEqual(prefix.prefix_suffix_from_strong_prefix_suffix(
        prefix.strong_prefix_suffix(t, n)), reference)

  def check_strong_prefix_suffix(self, t, n, reference):
    self.assertEqual(prefix.strong_prefix_suffix(t, n), reference)

  def check_prefix_prefix(self, t, n, reference):
    self.assertEqual(prefix.prefix_prefix_brute_force(t, n), reference)
    self.assertEqual(prefix.prefix_prefix(t, n), reference)

  def check_weak_boyer_moore_shift(self, t, n, reference):
    self.assertEqual(
        suffix.weak_boyer_moore_shift_brute_force(t, n), reference)
    self.assertEqual(suffix.weak_boyer_moore_shift(t, n), reference)

  def check_boyer_moore_shift(self, t, n, reference):
    self.assertEqual(suffix.boyer_moore_shift_brute_force(t, n), reference)
    self.assertEqual(suffix.boyer_moore_shift(t, n), reference)

  def test_prefix_suffix(self):
    self.check_prefix_suffix('#abaab', 5, [-1, 0, 0, 1, 1, 2])
    self.check_prefix_suffix(
        '#abababababb', 11, [-1, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 0])

  def test_strong_prefix_suffix(self):
    self.check_strong_prefix_suffix('#abaab', 5, [-1, 0, -1, 1, 0, 2])
    self.check_strong_prefix_suffix(
        '#abaababa', 8, [-1, 0, -1, 1, 0, -1, 3, -1, 3])

  def test_prefix_prefix(self):
    self.check_prefix_prefix('#abaab', 5, [-1, -1, 0, 1, 2, 0])
    self.check_prefix_prefix('#aabbaaab', 8, [-1, -1, 1, 0, 0, 2, 3, 1, 0])
    self.check_prefix_prefix('#abaa', 4, [-1, -1, 0, 1, 1])
    self.check_prefix_prefix('#aabb', 4, [-1, -1, 1, 0, 0])

  def test_boyer_moore_shift(self):
    self.check_boyer_moore_shift('#abaaba', 6, [3, 3, 3, 3, 5, 2, 1])

  @run_large
  def test_random_prefix_suffix(self):
    T, n, A = 200, 200, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      reference_result = prefix.prefix_suffix_brute_force(t, n)
      self.check_prefix_suffix(t, n, reference_result)

  @run_large
  def test_all_prefix_suffix(self):
    N, A = 15, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        reference_result = prefix.prefix_suffix_brute_force(t, n)
        self.check_prefix_suffix(t, n, reference_result)

  @run_large
  def test_random_prefix_prefix(self):
    T, n, A = 200, 200, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      reference_result = prefix.prefix_prefix_brute_force(t, n)
      self.check_prefix_prefix(t, n, reference_result)

  @run_large
  def test_all_prefix_prefix(self):
    N, A = 15, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        reference_result = prefix.prefix_prefix_brute_force(t, n)
        self.check_prefix_prefix(t, n, reference_result)

  @run_large
  def test_random_weak_boyer_moore_shift(self):
    T, n, A = 200, 200, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      reference_result = suffix.weak_boyer_moore_shift_brute_force(t, n)
      self.check_weak_boyer_moore_shift(t, n, reference_result)

  @run_large
  def test_all_weak_boyer_moore_shift(self):
    N, A = 14, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        reference_result = suffix.weak_boyer_moore_shift_brute_force(t, n)
        self.check_weak_boyer_moore_shift(t, n, reference_result)

  @run_large
  def test_random_boyer_moore_shift(self):
    T, n, A = 200, 200, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      reference_result = suffix.boyer_moore_shift_brute_force(t, n)
      self.check_boyer_moore_shift(t, n, reference_result)

  @run_large
  def test_all_boyer_moore_shift(self):
    N, A = 14, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        reference_result = suffix.boyer_moore_shift_brute_force(t, n)
        self.check_boyer_moore_shift(t, n, reference_result)
