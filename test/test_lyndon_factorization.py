import itertools
import os
import unittest

from generator import rand
from lyndon import lyndon_factorization

class TestLyndonFactorization(unittest.TestCase):
  run_large = unittest.skipUnless(
    os.environ.get('LARGE', False), 'Skip test in small runs')

  def compare_lyndon_factorization_with_reference(self, text, n, reference):
    factorization = list(lyndon_factorization.duval(text, n))
    lyndon_words = [text[begin:end] for (begin, end) in factorization]
    self.assertEqual(factorization, reference,
      f"Incorrect factorization {lyndon_words} for word: {text}")

  def check_lyndon_factorization(self, text, n):
    factorization = [text[begin:end]
                     for (begin, end) in lyndon_factorization.duval(text, n)]

    self.assertEqual("#" + "".join(factorization), text,
      f"Incorrect factorization {factorization} for word: {text}")

    for w in factorization:
      self.assertEqual(w, min(w[i:] for i in range(len(w))),
        f"Incorrect factorization {factorization} for word: {text}")

    for w1, w2 in zip(factorization[0:-1], factorization[1:]):
      self.assertTrue(w1 >= w2,
        f"Incorrect factorization {factorization} for word: {text}")

  def test_lyndon_factorization(self):
    self.compare_lyndon_factorization_with_reference(
      '#abaaba', 6, [(1, 3), (3, 6), (6, 7)])
    self.compare_lyndon_factorization_with_reference(
      '#banana', 6, [(1, 2), (2, 4), (4, 6), (6, 7)])
    self.compare_lyndon_factorization_with_reference(
      '#abaaaaa', 7, [(1, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8)])
    self.compare_lyndon_factorization_with_reference(
      '#yabbadabbado', 12, [(1, 2), (2, 13)])
    self.compare_lyndon_factorization_with_reference(
      '#aabaabaabba', 11, [(1, 11), (11, 12)])
    self.compare_lyndon_factorization_with_reference(
      '#eembambmaa', 10, [(1, 4), (4, 5), (5, 9), (9, 10), (10, 11)])
    self.compare_lyndon_factorization_with_reference(
      '#abcd', 4, [(1, 5)])

  @run_large
  def test_random_lyndon_factorization(self):
    T, n, A = 100, 300, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      self.check_lyndon_factorization(t, n)

  @run_large
  def test_all_lyndon_factorization(self):
    N, A = 14, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        self.check_lyndon_factorization(t, n)
