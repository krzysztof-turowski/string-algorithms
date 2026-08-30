import itertools
import os
import random
import unittest

from shortest_common_superstring import common


def brute_force_cycle_cover_cost(matrix, mode):
  n = len(matrix)
  best_cost = None
  for perm in itertools.permutations(range(n)):
    if n > 1 and any(perm[i] == i for i in range(n)):
      continue
    cost = sum(matrix[i][perm[i]] for i in range(n))
    if best_cost is None or (mode == 'min' and cost < best_cost) or \
       (mode == 'max' and cost > best_cost):
      best_cost = cost
  return best_cost


def cycles_cost(matrix, cycles):
  total = 0
  for cyc in cycles:
    L = len(cyc)
    for idx in range(L):
      total += matrix[cyc[idx]][cyc[(idx + 1) % L]]
  return total


class TestCycleCover(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_cycle_cover(self, matrix, mode):
    n = len(matrix)
    cycles = common.cycle_cover(matrix, mode=mode)
    covered = sorted(v for cyc in cycles for v in cyc)
    self.assertEqual(covered, list(range(n)),
                     f'matrix={matrix}, mode={mode}, cycles={cycles}')
    actual = cycles_cost(matrix, cycles)
    expected = brute_force_cycle_cover_cost(matrix, mode)
    self.assertEqual(actual, expected,
                     f'matrix={matrix}, mode={mode}, cycles={cycles}')

  def test_regression_small_close_weights_no_self_loops(self):
    self.check_cycle_cover([[13, 7], [6, 3]], 'min')
    self.check_cycle_cover([[3, 6], [7, 16]], 'min')
    self.check_cycle_cover([[10, 10], [10, 19]], 'min')

  def test_handmade_triangle(self):
    matrix = [[0, 5, 1], [1, 0, 5], [5, 1, 0]]
    self.check_cycle_cover(matrix, 'max')
    matrix2 = [[0, 1, 100], [100, 0, 1], [1, 100, 0]]
    self.check_cycle_cover(matrix2, 'min')

  def test_random_small(self):
    rng = random.Random(0)
    for _ in range(500):
      n = rng.randint(2, 6)
      matrix = [[rng.randint(-20, 20) for _ in range(n)] for _ in range(n)]
      for mode in ('min', 'max'):
        self.check_cycle_cover(matrix, mode)

  @run_large
  def test_random_small_extensive(self):
    rng = random.Random(1)
    for _ in range(5000):
      n = rng.randint(2, 7)
      matrix = [[rng.randint(-30, 30) for _ in range(n)] for _ in range(n)]
      for mode in ('min', 'max'):
        self.check_cycle_cover(matrix, mode)


class TestMaxWeightMatching(unittest.TestCase):

  def test_prefers_heavier_direction_and_pair(self):
    edges = {(0, 1): 5, (1, 0): 2, (1, 2): 3, (2, 1): 1, (0, 2): 1, (2, 0): 1}
    matching = common.max_weight_matching(edges)
    self.assertEqual(len(matching), 1)
    self.assertEqual(frozenset(matching[0]), frozenset((0, 1)))

  def test_handles_only_one_direction_present(self):
    edges = {(0, 1): 4, (2, 3): 9}
    matching = common.max_weight_matching(edges)
    pairs = {frozenset(e) for e in matching}
    self.assertEqual(pairs, {frozenset((0, 1)), frozenset((2, 3))})


if __name__ == '__main__':
  unittest.main()
