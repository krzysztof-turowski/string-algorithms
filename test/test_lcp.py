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
        farach.lcp_array(t, n),
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
