import os
import random
import unittest

from shortest_common_superstring import breslauer, common, kosaraju


def brute_overlap(s, t):
  limit = min(len(s), len(t)) - 1
  for k in range(limit, -1, -1):
    if k == 0 or s[-k:] == t[:k]:
      return k
  return 0


def period(s):
  return common.get_period(s)


def infinite_period(w):
  n = len(w)
  for p in range(1, n + 1):
    if n % p == 0 and w == w[:p] * (n // p):
      return p
  return n


def is_equivalent(s, w):
  fs, fw = s[:period(s)], w[:infinite_period(w)]
  return len(fs) == len(fw) and fs in (fw + fw)


class TestOmegaRotation(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_overlap_rotation_lemma(self, W, candidates):
    rotation = breslauer.get_omega_rotation(W)
    period_alpha = infinite_period(W)
    long_repeat = rotation * (
        max(1, max(len(c) for c in candidates) // len(W) + 3))
    for s in candidates:
      if is_equivalent(s, W):
        continue
      ov = brute_overlap(s, long_repeat)
      period_s = period(s)
      self.assertLess(ov, period_s + 0.5 * period_alpha + 1e-9,
                       f'W={W}, ->W={rotation}, s={s}, ov={ov}')
      if period_s <= period_alpha:
        self.assertLess(ov, (2 / 3) * (period_s + period_alpha) + 1e-9,
                         f'(stronger bound) W={W}, ->W={rotation}, '
                         f's={s}, ov={ov}')

  def test_handmade_periodic_strings(self):
    self.check_overlap_rotation_lemma(
        'ab', ['aab', 'bba', 'ba', 'abb', 'a', 'b'])
    self.check_overlap_rotation_lemma(
        'abc', ['cab', 'bca', 'abcab', 'ccc', 'aabbcc'])
    self.check_overlap_rotation_lemma('aab', ['baaa', 'aabaab', 'bab', 'aaab'])
    self.check_overlap_rotation_lemma('abaabaa', ['aabaaaba', 'aaabaaaba'])

  def test_random_periodic_strings(self):
    rng = random.Random(7)
    alphabet = ['a', 'b']
    for _ in range(200):
      period_len = rng.randint(1, 5)
      W = ''.join(rng.choice(alphabet) for _ in range(period_len))
      candidates = [''.join(rng.choice(alphabet)
                            for _ in range(rng.randint(1, 12)))
                    for _ in range(15)]
      self.check_overlap_rotation_lemma(W, candidates)

  @run_large
  def test_random_periodic_strings_large_alphabet(self):
    rng = random.Random(8)
    alphabet = ['a', 'b', 'c']
    for _ in range(2000):
      period_len = rng.randint(1, 8)
      W = ''.join(rng.choice(alphabet) for _ in range(period_len))
      candidates = [''.join(rng.choice(alphabet)
                            for _ in range(rng.randint(1, 20)))
                    for _ in range(20)]
      self.check_overlap_rotation_lemma(W, candidates)


class TestConstructTc(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_lemma_5_1(self, strings, cycle_indices):
    L = len(cycle_indices)
    t_c = breslauer.construct_tc(cycle_indices, strings)

    broken = [breslauer.build_broken_cycle_string(
        [cycle_indices[(bp + i) % L] for i in range(L)], strings)
        for bp in range(L)]

    found_i = any(broken[j] in t_c for j in range(L))
    self.assertTrue(found_i,
                     f'Lemma 5.1 condition (i) not satisfied: '
                     f't_c={t_c!r}, broken={broken!r}')

    W = ""
    for i in range(L):
      u = strings[cycle_indices[i]]
      v = strings[cycle_indices[(i + 1) % L]]
      ov = breslauer.get_overlap(u, v)
      W += u[:-ov] if ov > 0 else u
    omega = breslauer.get_omega_rotation(W)
    max_h_len = max(len(h) for h in broken)
    search_space = omega * ((max_h_len // len(omega)) + 3)

    winner_bp, earliest_start = None, float('inf')
    for bp, h in enumerate(broken):
      idx = search_space.find(h)
      if idx != -1 and idx < earliest_start:
        earliest_start, winner_bp = idx, bp
    self.assertIsNotNone(
        winner_bp, f'No break point found in ->omega^inf: {broken!r}')

    j = (winner_bp - 1) % L
    container_seq = ([cycle_indices[(j + i) % L] for i in range(L)]
                     + [cycle_indices[j]])
    container = breslauer.build_broken_cycle_string(container_seq, strings)
    self.assertIn(t_c, container,
                   f'Lemma 5.1 condition (ii) not satisfied: '
                   f't_c={t_c!r}, container={container!r}')

  def test_handmade_cycles(self):
    strings = ['abc', 'cde', 'efa']
    self.check_lemma_5_1(strings, [0, 1, 2])

  def test_random_cycles(self):
    rng = random.Random(9)
    alphabet = ['a', 'b', 'c']
    for _ in range(200):
      k = rng.randint(2, 6)
      strings = [''.join(rng.choice(alphabet) for _ in range(rng.randint(2, 8)))
                 for _ in range(k)]
      strings = breslauer.remove_substrings(strings)
      if len(strings) < 2:
        continue
      self.check_lemma_5_1(strings, list(range(len(strings))))


class TestOverlapAlgorithmParameter(unittest.TestCase):

  def test_default_matches_kosaraju_superstring(self):
    strings = ['#abc', '#bcf', '#fgh']
    result = breslauer.breslauer_jiang_jiang_by_overlap(strings)
    for s in strings:
      self.assertIn(s[1:], result)
    self.assertTrue(result.startswith('#'))

  def test_custom_overlap_algorithm_is_actually_invoked(self):
    calls = []

    def spy_algorithm(T):
      calls.append(list(T))
      return kosaraju.superstring(T)

    strings = ['#abc', '#bcf', '#fgh']
    breslauer.breslauer_jiang_jiang_by_overlap(
        strings, overlap_algorithm=spy_algorithm)
    self.assertEqual(len(calls), 1,
                     'overlap_algorithm should be called exactly once')

  def test_custom_overlap_algorithm_result_is_used(self):
    marker = 'THIS_IS_A_MARKER_VALUE'
    strings = ['#abc', '#bcf', '#fgh']
    result = breslauer.breslauer_jiang_jiang_by_overlap(
        strings, overlap_algorithm=lambda T: marker)
    self.assertEqual(result, '#' + marker)

  def test_random_custom_overlap_algorithm(self):
    rng = random.Random(11)
    alphabet = ['a', 'b', 'c']
    for _ in range(50):
      k = rng.randint(2, 6)
      strings = ['#' + ''.join(rng.choice(alphabet)
                               for _ in range(rng.randint(3, 8)))
                 for _ in range(k)]
      result = breslauer.breslauer_jiang_jiang_by_overlap(
          strings, overlap_algorithm=lambda T: ''.join(T))
      for s in strings:
        self.assertIn(s[1:], result, f'strings={strings}, result={result}')


if __name__ == '__main__':
  unittest.main()
