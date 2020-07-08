import itertools
import os
import unittest

from generator import rand
from string_indexing import suffix_tree, suffix_array, farach_suffix_tree, \
                            sl_suffix_array, lcp_lr, is_suffix_array, \
                            larsson_sadakane_suffix_array

SUFFIX_TREE_ALGORITHMS = [
    suffix_tree.weiner,
    suffix_tree.mccreight,
    suffix_tree.ukkonen,
    farach_suffix_tree.farach_suffix_tree,
]

SUFFIX_ARRAY_ALGORITHMS = [
    suffix_array.prefix_doubling,
    suffix_array.skew,
    farach_suffix_tree.farach_suffix_array,
    sl_suffix_array.small_large,
    is_suffix_array.sa_is,
    larsson_sadakane_suffix_array.larsson_sadakane_suffix_array
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
          'Algorithm: {0}'.format(algorithm.__name__))

  def check_suffix_links(self, t, n, reference):
    self.assertEqual(
        TestSuffixTrees.get_suffix_links(*suffix_tree.mccreight(t, n)),
        reference,
        'Algorithm: mccreight')
    self.assertEqual(
        TestSuffixTrees.get_suffix_links(*suffix_tree.ukkonen(t, n)),
        reference,
        'Algorithm: ukkonen')
    self.assertEqual(
        TestSuffixTrees.get_backward_suffix_links(*suffix_tree.weiner(t, n)),
        reference,
        'Algorithm: weiner')

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
          'Algorithm: {0}'.format(algorithm.__name__))
    self.assertEqual(
        suffix_array.from_suffix_tree(suffix_tree.mccreight(t, n)[0], n),
        reference,
        'Suffix tree from suffix array')

  def test_suffix_array(self):
    self.check_suffix_array('#abaaba', 6, [7, 6, 3, 4, 1, 5, 2])
    self.check_suffix_array('#banana', 6, [7, 6, 4, 2, 1, 5, 3])
    self.check_suffix_array('#abaaaaaaa', 9, [10, 9, 8, 7, 6, 5, 4, 3, 1, 2])
    self.check_suffix_array(
        '#yabbadabbado', 12, [13, 2, 7, 5, 10, 4, 9, 3, 8, 6, 11, 12, 1])
    self.check_suffix_array(
        '#aabaabaabba', 11, [12, 11, 1, 4, 7, 2, 5, 8, 10, 3, 6, 9])
    self.check_suffix_array(
        '#hcrgpfeargibbpq', 15,
        [16, 8, 12, 13, 2, 7, 6, 10, 4, 1, 11, 5, 14, 15, 9, 3])
    self.check_suffix_array(
        '#obdkbgaobg', 10, [11, 7, 2, 9, 5, 3, 10, 6, 4, 1, 8])

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

class TestLcpArrays(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_lcp_array(self, t, n, reference):
    self.assertEqual(
        suffix_array.lcp_from_suffix_array(
            suffix_array.prefix_doubling(t, n), t, n),
        reference,
        'LCP array from suffix array')
    self.assertEqual(
        suffix_array.lcp_from_suffix_tree(suffix_tree.mccreight(t, n)[0]),
        reference,
        'LCP array from suffix tree')
    self.assertEqual(
        suffix_array.lcp_kasai(suffix_array.prefix_doubling(t, n), t, n),
        reference,
        'Algorithm: kasai')
    self.assertEqual(
        farach_suffix_tree.farach_lcp_array(t, n),
        reference,
        'Algorithm: farach'
    )

  def test_lcp_array(self):
    self.check_lcp_array('#banana', 6, [-1, 0, 1, 3, 0, 0, 2])

  @run_large
  def test_random_lcp_array(self):
    T, n, A = 100, 500, ['a', 'b']
    for _ in range(T):
      t = rand.random_word(n, A)
      reference = suffix_array.lcp_from_suffix_array(
          suffix_array.prefix_doubling(t, n), t, n)
      self.check_lcp_array(t, n, reference)

  @run_large
  def test_all_lcp_array(self):
    N, A = 12, ['a', 'b']
    for n in range(2, N + 1):
      for t in itertools.product(A, repeat = n):
        t = '#' + ''.join(t)
        reference = suffix_array.lcp_from_suffix_array(
            suffix_array.prefix_doubling(t, n), t, n)
        self.check_lcp_array(t, n, reference)

class TestLcpLr(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def test_lcplr_construction(self):
    text = "#banana"
    n = len(text) - 1
    sa = suffix_array.skew(text, n)
    lcp = suffix_array.lcp_kasai(sa, text, n)
    lcplr = lcp_lr.lcplr_from_lcp(lcp, n)
    reference = {
        (1, 2): 1,
        (2, 3): 3,
        (1, 3): 1,
        (3, 4): 0,
        (4, 5): 0,
        (5, 6): 2,
        (4, 6): 0,
        (3, 6): 0,
        (1, 6): 0,
    }

    self.assertEqual(lcplr, reference, "LCP-LR construction")

  def test_lcplr_matching(self):
    text = "#abrakadabra"
    n = len(text) - 1
    sa = suffix_array.skew(text, n)
    lcp = suffix_array.lcp_kasai(sa, text, n)
    lcplr = lcp_lr.lcplr_from_lcp(lcp, n)

    self.assertEqual(list(lcp_lr.contains_with_lcplr(
        sa, lcplr, text, "#a", n, 1)), [1,4,6,8,11], "LCP-LR matching")
    self.assertEqual(list(lcp_lr.contains_with_lcplr(
        sa, lcplr, text, "#bra", n, 3)), [2,9], "LCP-LR matching")
    self.assertEqual(list(lcp_lr.contains_with_lcplr(
        sa, lcplr, text, "#brak", n, 4)), [2], "LCP-LR matching")
    self.assertEqual(list(lcp_lr.contains_with_lcplr(
        sa, lcplr, text, "#ra", n, 2)), [3,10], "LCP-LR matching")
    self.assertEqual(list(lcp_lr.contains_with_lcplr(
        sa, lcplr, text, "#rak", n, 3)), [3], "LCP-LR matching")
    self.assertEqual(list(lcp_lr.contains_with_lcplr(
        sa, lcplr, text, "#l", n, 1)), [], "LCP-LR matching")
    self.assertEqual(list(lcp_lr.contains_with_lcplr(
        sa, lcplr, text, "#x", n, 1)), [], "LCP-LR matching")
    self.assertEqual(list(lcp_lr.contains_with_lcplr(
        sa, lcplr, text, "#xyz", n, 3)), [], "LCP-LR matching")

  @run_large
  def test_random_lcp_lr_matching(self):
    T, n, A = 1000, 500, ['a', 'b']
    m, TT = 10, 10
    for _ in range(T):
      text = rand.random_word(n, A)
      sa = suffix_array.skew(text, n)
      lcp = suffix_array.lcp_kasai(sa, text, n)
      lcplr = lcp_lr.lcplr_from_lcp(lcp, n)

      for _ in range(TT):
        word = rand.random_word(m, A)
        reference = suffix_array.contains(sa, text, word, n, m)
        self.assertEqual(list(lcp_lr.contains_with_lcplr(
            sa, lcplr, text, word, n, m)), list(reference))
