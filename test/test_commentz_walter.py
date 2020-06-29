import unittest
import os
from random import randint

from exact_multiple_string_matching.commentz_walter import \
  commentz_walter_build, commentz_walter_search
from exact_string_matching.forward import brute_force
from generator.rand import random_word

class TestCommentzWalter(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def test_single_keyword(self):
    cw_automat = commentz_walter_build(['abc'])
    found = list(commentz_walter_search('aabccabcab', 10, cw_automat))
    correct = [
        ('abc', 1),
        ('abc', 5)
    ]
    self.assertListEqual(found, correct)

  def test_non_overlapping(self):
    cw_automat = commentz_walter_build(['aa', 'bcc', 'bcab'])
    found = list(commentz_walter_search('aabccabcab', 10, cw_automat))
    correct = [
        ('aa', 0),
        ('bcc', 2),
        ('bcab', 6)
    ]
    self.assertListEqual(found, correct)

  def test_overlapping(self):
    cw_automat = commentz_walter_build(['he', 'she', 'his', 'her', 'hers'])
    found = list(commentz_walter_search('eshers', 6, cw_automat))
    correct = [
        ('he', 2),
        ('she', 1),
        ('her', 2),
        ('hers', 2)
    ]
    self.assertListEqual(found, correct)

  def test_pessimistic(self):
    cw_automat = commentz_walter_build([i * 'a' for i in range(1, 6)])
    found = list(commentz_walter_search('a' * 20, 20, cw_automat))
    self.assertEqual(len(found), 20 + 19 + 18 + 17 + 16)

  def test_no_match(self):
    cw_automat = commentz_walter_build(['bb', 'abba'])
    found = list(commentz_walter_search('abababab', 8, cw_automat))
    self.assertFalse(list(found))

  def test_small(self):
    cw_automat = commentz_walter_build(
        ['cacbaa', 'acb', 'aba', 'acbab', 'ccbab'])
    found = list(commentz_walter_search('dacbaababababa', 14, cw_automat))
    correct = [
        ('acb', 1),
        ('aba', 5),
        ('aba', 7),
        ('aba', 9),
        ('aba', 11)
    ]
    self.assertListEqual(found, correct)

  def test_random_small(self):
    n, m, A = 100, 25, ['a', 'b', 'c']
    for _ in range(100):
      t = random_word(n, A)
      patterns = {(random_word(randint(2, 5), A)) for _ in range(m)}
      cw_automat = commentz_walter_build(patterns)

      expected = set()
      for p in patterns:
        starts = brute_force(t, p, n, len(p) - 1)
        indices = [(p, i) for i in starts]
        expected.union(set(indices))

      found = set(commentz_walter_search(t[1::], n, cw_automat))
      self.assertSetEqual(expected, found)

  @run_large
  def test_random_big(self):
    n, m, A = 1000, 100, ['a', 'b', 'c']
    for _ in range(100):
      t = random_word(n, A)
      patterns = {random_word(randint(2, 5), A) for _ in range(m)}
      cw_automat = commentz_walter_build(patterns)

      expected = set()
      for p in patterns:
        starts = brute_force(t, p, n, len(p) - 1)
        indices = [(p, i) for i in starts]
        expected.union(set(indices))

      found = set(commentz_walter_search(t[1::], n, cw_automat))

      self.assertSetEqual(expected, found)
