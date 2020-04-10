import itertools
import os
import unittest

from generator import rand
from string_indexing import suffix_tree, suffix_array

SUFFIX_TREE_ALGORITHMS = [
    suffix_tree.weiner,
    suffix_tree.mccreight,
    suffix_tree.ukkonen,
]

SUFFIX_ARRAY_ALGORITHMS = [
    suffix_array.prefix_doubling,
]

class TestSuffixTrees(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  @staticmethod
  def get_suffix_links(tree, links):
    tree.set_index()
    return tree, sorted([(u.index, v.index) for u, v in links.items()])

  @staticmethod
  def get_backward_suffix_links(tree, links):
    tree.set_index()
    return tree, sorted([(v.index, u.index) for (u, _), v in links.items()])

  def check_suffix_trees(self, t, n, reference):
    for algorithm in SUFFIX_TREE_ALGORITHMS:
      self.assertEqual(
          algorithm(t, n)[0],
          reference,
          "Algorithm: {0}".format(algorithm.__name__))

  def check_suffix_links(self, t, n, reference):
    self.assertEqual(
        TestSuffixTrees.get_suffix_links(*suffix_tree.mccreight(t, n)),
        reference,
        "Algorithm: McCreight")
    self.assertEqual(
        TestSuffixTrees.get_suffix_links(*suffix_tree.ukkonen(t, n)),
        reference,
        "Algorithm: Ukkonen")
    self.assertEqual(
        TestSuffixTrees.get_backward_suffix_links(*suffix_tree.weiner(t, n)),
        reference,
        "Algorithm: Weiner")

  @run_large
  def test_random_suffix_tree(self):
    T, n, A = 100, 200, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      reference = suffix_tree.naive(t, n)
      self.check_suffix_trees(t, n, reference)

  @run_large
  def test_all_suffix_tree(self):
    N, A = 10, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        reference = suffix_tree.naive(t, n)
        self.check_suffix_trees(t, n, reference)

  @run_large
  def test_random_suffix_links(self):
    T, n, A = 100, 200, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      reference = TestSuffixTrees.get_suffix_links(
          *suffix_tree.mccreight(t, n))
      self.check_suffix_links(t, n, reference)

  @run_large
  def test_all_suffix_links(self):
    N, A = 10, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        reference = TestSuffixTrees.get_suffix_links(
            *suffix_tree.mccreight(t, n))
        self.check_suffix_links(t, n, reference)

class TestSuffixArrays(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_suffix_array(self, t, n, reference):
    for algorithm in SUFFIX_ARRAY_ALGORITHMS:
      self.assertEqual(
          algorithm(t, n),
          reference,
          "Algorithm: {0}".format(algorithm.__name__))
    self.assertEqual(
        suffix_array.from_suffix_tree(suffix_tree.mccreight(t, n)[0], n),
        reference,
        "Suffix tree from suffix array")

  def test_suffix_array(self):
    self.check_suffix_array("#abaaba", 6, [7, 6, 3, 4, 1, 5, 2])
    self.check_suffix_array("#banana", 6, [7, 6, 4, 2, 1, 5, 3])

  @run_large
  def test_random_suffix_array(self):
    T, n, A = 100, 500, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      reference = suffix_array.naive(t, n)
      self.check_suffix_array(t, n, reference)

  @run_large
  def test_all_suffix_array(self):
    N, A = 12, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        reference = suffix_array.naive(t, n)
        self.check_suffix_array(t, n, reference)
