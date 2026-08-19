import itertools
import os
import random
import unittest

from shortest_common_superstring import kosaraju, common


def make_complete_graph(n, max_weight, rng):
  V = list(range(n))
  E = [(i, j) for i in V for j in V if i != j]
  weights = {(i, j): rng.randint(0, max_weight) for i, j in E}
  return V, E, weights


def brute_force_topt(V, weights):
  best = 0
  for perm in itertools.permutations(V):
    w = sum(weights[(perm[i], perm[(i + 1) % len(perm)])] for i in range(len(perm)))
    best = max(best, w)
  return best


def cycle_bcw(solver, C):
  W = sum(solver.w(*e) for cycle in C for e in cycle)
  if W == 0:
    return 0.0, 0.0, 0.0
  b = c = 0.0
  for cycle in C:
    if len(cycle) == 2:
      w1, w2 = solver.w(*cycle[0]), solver.w(*cycle[1])
      b += max(w1, w2) / W
      c += min(w1, w2) / W
  return b, c, W


def assert_vertex_disjoint_paths(test, V, P):
  out_deg, in_deg = {}, {}
  for u, v in P:
    out_deg[u] = out_deg.get(u, 0) + 1
    in_deg[v] = in_deg.get(v, 0) + 1
    test.assertLessEqual(out_deg[u], 1, f'vertex {u} has out-degree > 1 in P={P}')
    test.assertLessEqual(in_deg[v], 1, f'vertex {v} has in-degree > 1 in P={P}')


def is_valid_tour(V, tour):
  if len(tour) != len(V) or not V:
    return False
  out_of = {}
  for u, v in tour:
    if u in out_of:
      return False
    out_of[u] = v
  if set(out_of) != set(V):
    return False
  start = V[0]
  visited = {start}
  curr = out_of[start]
  while curr != start:
    if curr in visited:
      return False
    visited.add(curr)
    curr = out_of[curr]
  return len(visited) == len(V)


class TestKosaraju(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def test_compute_max_weight_cycle_cover_handmade(self):
    V = [0, 1, 2]
    E = [(i, j) for i in V for j in V if i != j]
    weights = {(0, 1): 5, (1, 2): 5, (2, 0): 5,
               (1, 0): 1, (2, 1): 1, (0, 2): 1}
    solver = kosaraju.DirectedMaxTSPApproximation(V, E, weights)
    C = solver.compute_max_weight_cycle_cover()
    self.assertEqual(len(C), 1)
    self.assertEqual(set(C[0]), {(0, 1), (1, 2), (2, 0)})

  def check_version_bound(self, version_method, formula, n_low, n_high, rng, trials):
    for _ in range(trials):
      n = rng.randint(n_low, n_high)
      V, E, weights = make_complete_graph(n, 20, rng)
      solver = kosaraju.DirectedMaxTSPApproximation(V, E, weights)
      C = solver.compute_max_weight_cycle_cover()
      b, c, _ = cycle_bcw(solver, C)
      P = version_method(solver, C)
      assert_vertex_disjoint_paths(self, V, P)
      tour = solver.patch_paths_to_tour(P)
      self.assertTrue(is_valid_tour(solver.V, tour), f'n={n}, tour={tour}')
      w_tour = sum(solver.w(*e) for e in tour)
      topt = brute_force_topt(V, weights)
      bound = formula(b, c) * topt
      self.assertGreaterEqual(w_tour + 1e-9, bound,
                               f'n={n}, b={b}, c={c}, topt={topt}, w(tour)={w_tour}, bound={bound}')

  def test_version_1_bound(self):
    rng = random.Random(1)
    self.check_version_bound(
        lambda solver, C: solver.version_1(C),
        lambda b, c: 2 / 3 + 1 / 3 * (b - 2 * c), 4, 8, rng, 100)

  def test_version_1_bound_all_two_cycles(self):
    V = [0, 1, 2, 3]
    weights = {(0, 1): 4, (1, 0): 4, (2, 3): 6, (3, 2): 6}
    E = list(weights.keys())
    solver = kosaraju.DirectedMaxTSPApproximation(V, E, weights)
    C = [[(0, 1), (1, 0)], [(2, 3), (3, 2)]]
    b, c, W = cycle_bcw(solver, C)
    self.assertAlmostEqual(b, 0.5)
    self.assertAlmostEqual(c, 0.5)
    P = solver.version_1(C)
    tour = solver.patch_paths_to_tour(P)
    w_tour = sum(solver.w(*e) for e in tour)
    bound = (2 / 3 + 1 / 3 * (b - 2 * c)) * W
    self.assertAlmostEqual(bound, 0.5 * W)
    self.assertGreaterEqual(w_tour + 1e-9, bound)

  @run_large
  def test_version_2_real_variant_bound(self):
    rng = random.Random(2)
    self.check_version_bound(
        lambda solver, C: solver.version_2_real_variant(C),
        lambda b, c: 7 / 12 - 1 / 12 * (b - 2 * c), 4, 8, rng, 60)

  def test_version_2_satisfies_lemma_3_preconditions(self):
    rng = random.Random(0)
    for _ in range(500):
      n = rng.randint(4, 14)
      V, E, weights = make_complete_graph(n, 20, rng)
      solver = kosaraju.DirectedMaxTSPApproximation(V, E, weights)
      C = solver.compute_max_weight_cycle_cover()
      contracted_V, contracted_E, _, _ = solver.build_contracted_graph_for_version_2(C)
      final_V, final_E, _ = solver._eliminate_induced_2_cycles(contracted_V, contracted_E)
      self.assert_lemma_3_preconditions(final_V, final_E, n)

  def assert_lemma_3_preconditions(self, V, E, n):
    E = set(E)
    indeg, outdeg = {}, {}
    for u, v in E:
      outdeg[u] = outdeg.get(u, 0) + 1
      indeg[v] = indeg.get(v, 0) + 1
      self.assertNotIn((v, u), E, f'n={n}, 2-cycle: ({u},{v}) and ({v},{u}) in E={E}')
    for v in V:
      i, o = indeg.get(v, 0), outdeg.get(v, 0)
      self.assertLessEqual(i, 2, f'n={n}, vertex {v}: indegree={i} > 2')
      self.assertLessEqual(o, 2, f'n={n}, vertex {v}: outdegree={o} > 2')
      self.assertLessEqual(i + o, 3, f'n={n}, vertex {v}: total degree={i + o} > 3')

  @run_large
  def test_version_3_real_variant_bound(self):
    rng = random.Random(3)
    self.check_version_bound(
        lambda solver, C: solver.version_3_real_variant(C),
        lambda b, c: 2 / 3 + 4 / 15 * (b - 2 * c), 4, 8, rng, 60)

  @run_large
  def test_version_3_real_variant_piece_size_and_disjoint(self):
    rng = random.Random(3)
    for _ in range(30):
      n = rng.randint(8, 16)
      V, E, weights = make_complete_graph(n, 20, rng)
      solver = kosaraju.DirectedMaxTSPApproximation(V, E, weights)
      C = solver.compute_max_weight_cycle_cover()
      P = solver.version_3_real_variant(C)
      assert_vertex_disjoint_paths(self, V, P)

  @run_large
  def test_run_returns_valid_hamiltonian_tour(self):
    rng = random.Random(4)
    for _ in range(300):
      n = rng.randint(4, 12)
      V, E, weights = make_complete_graph(n, 20, rng)
      solver = kosaraju.DirectedMaxTSPApproximation(V, E, weights)
      tour = solver.run()
      self.assertTrue(is_valid_tour(solver.V, tour), f'n={n}, tour={tour}')

  @run_large
  def test_run_returns_valid_hamiltonian_tour_more_iterations(self):
    rng = random.Random(42)
    for _ in range(3000):
      n = rng.randint(4, 15)
      V, E, weights = make_complete_graph(n, 20, rng)
      solver = kosaraju.DirectedMaxTSPApproximation(V, E, weights)
      tour = solver.run()
      self.assertTrue(is_valid_tour(solver.V, tour), f'n={n}, tour={tour}')

  def test_run_versions_subset_returns_valid_tour(self):
    rng = random.Random(7)
    for versions in [(1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]:
      for _ in range(15):
        n = rng.randint(4, 10)
        V, E, weights = make_complete_graph(n, 20, rng)
        solver = kosaraju.DirectedMaxTSPApproximation(V, E, weights)
        tour = solver.run(versions=versions)
        self.assertTrue(is_valid_tour(solver.V, tour),
                         f'versions={versions}, n={n}, tour={tour}')

  def test_run_versions_rejects_invalid_input(self):
    V, E, weights = make_complete_graph(5, 20, random.Random(8))
    solver = kosaraju.DirectedMaxTSPApproximation(V, E, weights)
    with self.assertRaises(ValueError):
      solver.run(versions=())
    with self.assertRaises(ValueError):
      solver.run(versions=(4,))

  def test_superstring_versions_argument_is_forwarded(self):
    rng = random.Random(9)
    alphabet = ['a', 'b', 'c']
    for versions in [(1,), (2,), (3,)]:
      strings = [''.join(rng.choice(alphabet) for _ in range(rng.randint(3, 8)))
                 for _ in range(rng.randint(3, 6))]
      strings = list(dict.fromkeys(strings))
      if len(strings) < 2:
        continue
      result = kosaraju.superstring(strings, versions=versions)
      for s in strings:
        self.assertIn(s, result, f'versions={versions}, strings={strings}, result={result}')

  def test_superstring_contains_all_inputs(self):
    rng = random.Random(5)
    alphabet = ['a', 'b', 'c', 'd']
    for _ in range(50):
      k = rng.randint(2, 8)
      strings = [''.join(rng.choice(alphabet) for _ in range(rng.randint(3, 12)))
                 for _ in range(k)]
      result = kosaraju.superstring(strings)
      for s in strings:
        self.assertIn(s, result, f'strings={strings}, result={result}')

  @run_large
  def test_superstring_38_63_bound(self):
    rng = random.Random(6)
    alphabet = ['a', 'b', 'c']
    bound = lambda n: (2 + 50 / 63) * n
    for _ in range(20):
      k = rng.randint(4, 8)
      strings = [''.join(rng.choice(alphabet) for _ in range(rng.randint(2, 6)))
                 for _ in range(k)]
      strings = list(dict.fromkeys(strings))
      if len(strings) < 2:
        continue
      result = kosaraju.superstring(strings)
      opt_upper_bound = sum(len(s) for s in strings)
      self.assertLessEqual(len(result), bound(opt_upper_bound),
                            f'strings={strings}, result={result}')


if __name__ == '__main__':
  unittest.main()
