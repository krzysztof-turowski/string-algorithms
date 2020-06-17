import unittest
from random import randint

from exact_multiple_string_matching.aho_corasick import \
  create_aho_corasick_automaton, find_occurrences
from exact_string_matching.forward import brute_force
from generator.rand import random_word


class TestAhoCorasick(unittest.TestCase):
  def test_single_keyword(self):
    text, n = '#aabccabcab', 10
    automaton = self._create_from(['abc'])

    found = list(find_occurrences(text, n, automaton))
    self.assertListEqual(found, [(2, 5), (6, 9)])

  def test_non_overlapping(self):
    text, n = '#aabccabcab', 10
    automaton = self._create_from(['aa', 'bcc', 'bcab'])

    found = list(find_occurrences(text, n, automaton))
    self.assertListEqual(found, [(1, 3), (3, 6), (7, 11)])

  def test_overlapping(self):
    text, n = '#eshers', 6
    automaton = self._create_from(['he', 'she', 'his', 'her', 'hers'])

    found = set(find_occurrences(text, n, automaton))
    self.assertSetEqual(found, {(2, 5), (3, 5), (3, 6), (3, 7)})

  def test_pessimistic(self):
    text, n = '#' + 'a' * 20, 20
    automaton = self._create_from([i * 'a' for i in range(1, 6)])

    found = set(find_occurrences(text, n, automaton))
    self.assertEqual(len(found), 20 + 19 + 18 + 17 + 16)

  def test_no_match(self):
    text, n = '#abababab', 8
    automaton = self._create_from(['bb', 'abba'])

    self.assertFalse(list(find_occurrences(text, n, automaton)))

  def test_random(self):
    n, m, A = 500, 30, ['a', 'b', 'c']
    for _ in range(100):
      t = random_word(n, A)
      patterns = {random_word(randint(2, 10), A) for _ in range(m)}
      automaton = self._create_from(patterns)

      expected = set()
      for p in patterns:
        starts = brute_force(t, f'#{p}', n, len(p) + 1)
        indices = map(lambda i: (i, i + len(p)), starts)
        expected.union(set(indices))

      found = set(find_occurrences(t, n, automaton))

      self.assertSetEqual(expected, found)

  @staticmethod
  def _create_from(patterns):
    keywords = [(f'#{p}', len(p)) for p in patterns]
    alphabet = {a for p in patterns for a in p}
    return create_aho_corasick_automaton(keywords, alphabet)
