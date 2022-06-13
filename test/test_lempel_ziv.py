import itertools
import os
import unittest
import string

from compression import lempel_ziv
from generator import rand

class TestLempelZiv77(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_factorization(self, text, reference, algorithm):
    self.assertEqual(algorithm('#' + text, len(text)), reference)

  def check_all_factorizations(self, text, reference=None):
    reference =  reference if reference is not None \
      else lempel_ziv.naive_factorization('#' + text, len(text))
    self.check_factorization(text, reference,
                             lempel_ziv.naive_factorization)
    self.check_factorization(text, reference,
                             lempel_ziv.crochemore_ilie_smyth)

  def test_lz_factorization_corners(self):
    # Example from
    #   "Linear time Lempel-Ziv Factorization: Simple, Fast, Small"
    #    page 3
    self.check_all_factorizations('zzzzzipzip',
                                  [(1, 0, 'z'),
                                   (2, 4, 'z'),
                                   (6, 0, 'i'),
                                   (7, 0, 'p'),
                                   (8, 3, 'z')])

    # Example from
    #  "A simple algorithm for computing the Lempel-Ziv factorization"
    #  page 1
    self.check_all_factorizations('abbaabbbaaabab',
                                  [(1, 0, 'a'),
                                   (2, 0, 'b'),
                                   (3, 1, 'b'),
                                   (4, 1, 'a'),
                                   (5, 3, 'a'),
                                   (8, 3, 'b'),
                                   (11, 2, 'a'),
                                   (13, 2, 'a')])

    self.check_all_factorizations('', [])
    self.check_all_factorizations('a', [(1, 0, 'a')])
    self.check_all_factorizations('aa', [(1, 0, 'a'), (2, 1, 'a')])
    self.check_all_factorizations('ab', [(1, 0, 'a'), (2, 0, 'b')])
    self.check_all_factorizations('aaaa', [(1, 0, 'a'), (2, 3, 'a')])
    self.check_all_factorizations('abab', [(1, 0, 'a'), (2, 0, 'b'),
                                           (3, 2, 'a')])
    self.check_all_factorizations('ababcbababaa')
    self.check_all_factorizations('eacacad')
    self.check_all_factorizations('aacaacabcabaaac')
    self.check_all_factorizations('abaab')
    self.check_all_factorizations('ababcbababaa')
    self.check_all_factorizations('aabbbbc')

  @run_large
  def test_lz_factorization_random(self):
    T, n, A = 100, 500, ['a', 'b', 'c']
    for _ in range(T):
      text = rand.random_word(n, A)[1:]
      self.check_all_factorizations(text)

  @run_large
  def test_lz_factorization_random_short_strings(self):
    T, n, A = 5, 500, ['a', 'b', 'c']
    for _ in range(T):
      text = rand.random_word(n, A)[1:]
      self.check_all_factorizations(text)

  @run_large
  def test_lz_factorization_random_cyclic(self):
    T, n, A = 10, 200, ['a', 'b', 'c']
    for _ in range(T):
      text = rand.random_word(n, A)[1:]
      text = text * 10
      self.check_all_factorizations(text)

  @run_large
  def test_lz_factorization_random_big_alphabet(self):
    T, n, A = 100, 500, string.ascii_letters + string.digits
    for _ in range(T):
      text = rand.random_word(n, A)[1:]
      self.check_all_factorizations(text)

  def check_lempel_ziv_77(self, t, n, reference):
    self.assertEqual(lempel_ziv.lz77(t, n), reference)

  def check_recode_lempel_ziv_77(self, t, n):
    self.assertEqual(lempel_ziv.inverse_lz77(lempel_ziv.lz77(t, n)), t)

  def test_lempel_ziv_77(self):
    self.check_lempel_ziv_77(
        '#ababcbababaa', 12,
        [(0, 0, 'a'), (0, 0, 'b'), (2, 2, 'c'), (4, 3, 'a'), (2, 2, 'a')])
    self.check_lempel_ziv_77(
        '#aacaacabcabaaac', 15,
        [(0, 0, 'a'), (1, 1, 'c'), (3, 4, 'b'), (3, 3, 'a'), (1, 2, 'c')])

  def test_recode_lempel_ziv_77(self):
    self.check_recode_lempel_ziv_77('#ababcbababaa', 12)
    self.check_recode_lempel_ziv_77('#aacaacabcabaaac', 15)

  @run_large
  def test_random_recode_lempel_ziv_77(self):
    T, n, A = 100, 500, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      self.check_recode_lempel_ziv_77(t, n)

  @run_large
  def test_all_recode_lempel_ziv_77(self):
    N, A = 12, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        self.check_recode_lempel_ziv_77(t, n)
