import itertools
import os
import unittest

import parameterized

from generator import rand
from string_indexing import farach, suffix_tree

def get_suffix_links(tree, links):
  tree.set_index()
  return tree, sorted([(u.index, v.index) for u, v in links.items()])

def get_backward_suffix_links(tree, links):
  tree.set_index()
  return tree, sorted([(v.index, u.index) for (u, _), v in links.items()])

SUFFIX_TREE_ALGORITHMS = [
    [
        'Weiner',
        suffix_tree.weiner,
        get_backward_suffix_links,
    ],
    [
        'McCreight',
        suffix_tree.mccreight,
        get_suffix_links,
    ],
    [
        'Ukkonen',
        suffix_tree.ukkonen,
        get_suffix_links,
    ],
    [
        'Farach',
        farach.suffix_tree,
        None,
    ]
]

class TestSuffixTrees(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_suffix_trees(self, t, n, reference, algorithm, links):
    result = algorithm(t, n)
    self.assertEqual(result[0], reference[0])
    if links is not None:
      self.assertEqual(links(*result), reference)

  @parameterized.parameterized.expand(SUFFIX_TREE_ALGORITHMS)
  @run_large
  def test_random_suffix_tree(self, _, algorithm, links):
    T, n, A = 100, 200, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      reference = (
          suffix_tree.naive(t, n),
          get_suffix_links(*suffix_tree.mccreight(t, n))[1])
      self.check_suffix_trees(t, n, reference, algorithm, links)

  @parameterized.parameterized.expand(SUFFIX_TREE_ALGORITHMS)
  @run_large
  def test_all_suffix_tree(self, _, algorithm, links):
    N, A = 10, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        reference = (
            suffix_tree.naive(t, n),
            get_suffix_links(*suffix_tree.mccreight(t, n))[1])
        self.check_suffix_trees(t, n, reference, algorithm, links)
