import itertools
import os
import random
import unittest

from shortest_common_superstring import kosaraju, shortest_common_superstring


def make_complete_graph(n, max_weight, rng):
  V = list(range(n))
  E = [(i, j) for i in V for j in V if i != j]
  weights = {(i, j): rng.randint(0, max_weight) for i, j in E}
  return V, E, weights


def brute_force_topt(V, weights):
  best = 0
  for perm in itertools.permutations(V):
    w = sum(weights[(perm[i], perm[(i + 1) % len(perm)])]
            for i in range(len(perm)))
    best = max(best, w)
  return best


def edge_weight(weights, e):
  return weights.get(e, 0)


def cycle_bcw(weights, C):
  W = sum(edge_weight(weights, e) for cycle in C for e in cycle)
  if W == 0:
    return 0.0, 0.0, 0.0
  b = c = 0.0
  for cycle in C:
    if len(cycle) == 2:
      w1, w2 = edge_weight(weights, cycle[0]), edge_weight(weights, cycle[1])
      b += max(w1, w2) / W
      c += min(w1, w2) / W
  return b, c, W


def assert_vertex_disjoint_paths(test, V, P):
  out_deg, in_deg = {}, {}
  for u, v in P:
    out_deg[u] = out_deg.get(u, 0) + 1
    in_deg[v] = in_deg.get(v, 0) + 1
    test.assertLessEqual(out_deg[u], 1,
                         f'vertex {u} has out-degree > 1 in P={P}')
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

  def test_max_weight_cycle_cover_handmade(self):
    V = [0, 1, 2]
    weights = {(0, 1): 5, (1, 2): 5, (2, 0): 5,
               (1, 0): 1, (2, 1): 1, (0, 2): 1}
    C = kosaraju._max_weight_cycle_cover(V, weights)
    self.assertEqual(len(C), 1)
    self.assertEqual(set(C[0]), {(0, 1), (1, 2), (2, 0)})

  def check_version_bound(self, version_method, formula, n_low, n_high, rng,
                          trials):
    for _ in range(trials):
      n = rng.randint(n_low, n_high)
      V, E, weights = make_complete_graph(n, 20, rng)
      C = kosaraju._max_weight_cycle_cover(V, weights)
      b, c, _ = cycle_bcw(weights, C)
      P = version_method(V, E, weights, C)
      assert_vertex_disjoint_paths(self, V, P)
      tour = kosaraju._patch_paths_to_tour(V, P)
      self.assertTrue(is_valid_tour(V, tour), f'n={n}, tour={tour}')
      w_tour = sum(edge_weight(weights, e) for e in tour)
      topt = brute_force_topt(V, weights)
      bound = formula(b, c) * topt
      self.assertGreaterEqual(w_tour + 1e-9, bound,
                               f'n={n}, b={b}, c={c}, topt={topt}, '
                               f'w(tour)={w_tour}, bound={bound}')

  def test_version_1_bound(self):
    rng = random.Random(1)
    self.check_version_bound(
        lambda V, E, weights, C: kosaraju.version_1(weights, C),
        lambda b, c: 2 / 3 + 1 / 3 * (b - 2 * c), 4, 8, rng, 100)

  def test_version_1_bound_all_two_cycles(self):
    V = [0, 1, 2, 3]
    weights = {(0, 1): 4, (1, 0): 4, (2, 3): 6, (3, 2): 6}
    C = [[(0, 1), (1, 0)], [(2, 3), (3, 2)]]
    b, c, W = cycle_bcw(weights, C)
    self.assertAlmostEqual(b, 0.5)
    self.assertAlmostEqual(c, 0.5)
    P = kosaraju.version_1(weights, C)
    tour = kosaraju._patch_paths_to_tour(V, P)
    w_tour = sum(edge_weight(weights, e) for e in tour)
    bound = (2 / 3 + 1 / 3 * (b - 2 * c)) * W
    self.assertAlmostEqual(bound, 0.5 * W)
    self.assertGreaterEqual(w_tour + 1e-9, bound)

  @run_large
  def test_version_2_real_variant_bound(self):
    rng = random.Random(2)
    self.check_version_bound(
        lambda V, E, weights, C: kosaraju.version_2_real_variant(V, weights, C),
        lambda b, c: 7 / 12 - 1 / 12 * (b - 2 * c), 4, 8, rng, 60)

  def test_version_2_satisfies_lemma_3_preconditions(self):
    rng = random.Random(0)
    for _ in range(500):
      n = rng.randint(4, 14)
      V, E, weights = make_complete_graph(n, 20, rng)
      C = kosaraju._max_weight_cycle_cover(V, weights)
      contracted, _ = kosaraju._build_contracted_graph_for_version_2(
          V, weights, C)
      final, _ = kosaraju._reduce_for_path_coloring(contracted)
      self.assert_lemma_3_preconditions(final, n)

  def test_version_2_keeps_half_of_the_step_2e_weight(self):
    rng = random.Random(3)
    for _ in range(200):
      n = rng.randint(4, 9)
      V, E, weights = make_complete_graph(n, 20, rng)
      C = kosaraju._max_weight_cycle_cover(V, weights)
      contracted, _ = kosaraju._build_contracted_graph_for_version_2(
          V, weights, C)
      alpha = sum(edge_weight(weights, data['original'])
                  for *_, data in contracted.edges(data=True))
      P = kosaraju.version_2_real_variant(V, weights, C)
      w_P = sum(edge_weight(weights, e) for e in P)
      self.assertGreaterEqual(
          w_P + 1e-9, alpha / 2,
          f'n={n}, w(P)={w_P} < alpha/2={alpha / 2}')

  def assert_lemma_3_preconditions(self, graph, n):
    for u, v in graph.edges():
      self.assertFalse(
          graph.has_edge(v, u),
          f'n={n}, 2-cycle: ({u},{v}) and ({v},{u}) in {list(graph.edges())}')
    for v in graph.nodes():
      i, o = graph.in_degree(v), graph.out_degree(v)
      self.assertLessEqual(i, 2, f'n={n}, vertex {v}: indegree={i} > 2')
      self.assertLessEqual(o, 2, f'n={n}, vertex {v}: outdegree={o} > 2')
      self.assertLessEqual(
          i + o, 3, f'n={n}, vertex {v}: total degree={i + o} > 3')

  @run_large
  def test_version_3_real_variant_bound(self):
    rng = random.Random(3)
    self.check_version_bound(
        lambda V, E, weights, C: kosaraju.version_3_real_variant(E, weights, C),
        lambda b, c: 2 / 3 + 4 / 15 * (b - 2 * c), 4, 8, rng, 60)

  @run_large
  def test_version_3_real_variant_piece_size_and_disjoint(self):
    rng = random.Random(3)
    for _ in range(30):
      n = rng.randint(8, 16)
      V, E, weights = make_complete_graph(n, 20, rng)
      C = kosaraju._max_weight_cycle_cover(V, weights)
      P = kosaraju.version_3_real_variant(E, weights, C)
      assert_vertex_disjoint_paths(self, V, P)

  @run_large
  def test_max_tsp_tour_returns_valid_hamiltonian_tour(self):
    rng = random.Random(4)
    for _ in range(300):
      n = rng.randint(4, 12)
      V, E, weights = make_complete_graph(n, 20, rng)
      tour = kosaraju.max_tsp_tour(V, E, weights)
      self.assertTrue(is_valid_tour(V, tour), f'n={n}, tour={tour}')

  @run_large
  def test_max_tsp_tour_returns_valid_hamiltonian_tour_more_iterations(self):
    rng = random.Random(42)
    for _ in range(3000):
      n = rng.randint(4, 15)
      V, E, weights = make_complete_graph(n, 20, rng)
      tour = kosaraju.max_tsp_tour(V, E, weights)
      self.assertTrue(is_valid_tour(V, tour), f'n={n}, tour={tour}')

  def test_max_tsp_tour_versions_subset_returns_valid_tour(self):
    rng = random.Random(7)
    for versions in [(1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]:
      for _ in range(15):
        n = rng.randint(4, 10)
        V, E, weights = make_complete_graph(n, 20, rng)
        tour = kosaraju.max_tsp_tour(V, E, weights, versions=versions)
        self.assertTrue(is_valid_tour(V, tour),
                         f'versions={versions}, n={n}, tour={tour}')

  def test_max_tsp_tour_odd_vertex_count(self):
    rng = random.Random(11)
    for n in [1, 3, 5, 7, 9, 11]:
      V, E, weights = make_complete_graph(n, 20, rng)
      tour = kosaraju.max_tsp_tour(V, E, weights)
      self.assertTrue(is_valid_tour(V, tour), f'n={n}, tour={tour}')
      leaked = [x for edge in tour for x in edge if x not in V]
      self.assertEqual(leaked, [], f'n={n}, dummy vertex leaked into {tour}')

  def test_max_tsp_tour_versions_rejects_invalid_input(self):
    V, E, weights = make_complete_graph(5, 20, random.Random(8))
    with self.assertRaises(ValueError):
      kosaraju.max_tsp_tour(V, E, weights, versions=())
    with self.assertRaises(ValueError):
      kosaraju.max_tsp_tour(V, E, weights, versions=(4,))

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
        self.assertIn(
            s, result,
            f'versions={versions}, strings={strings}, result={result}')

  def test_superstring_contains_all_inputs(self):
    rng = random.Random(5)
    alphabet = ['a', 'b', 'c', 'd']
    for _ in range(50):
      k = rng.randint(2, 8)
      strings = [''.join(rng.choice(alphabet)
                         for _ in range(rng.randint(3, 12)))
                 for _ in range(k)]
      result = kosaraju.superstring(strings)
      for s in strings:
        self.assertIn(s, result, f'strings={strings}, result={result}')

  def test_superstring_38_63_bound(self):
    rng = random.Random(6)
    alphabet = ['a', 'b']
    bound = lambda opt: (2 + 50 / 63) * opt
    for _ in range(100):
      k = rng.randint(3, 4)
      strings = [''.join(rng.choice(alphabet) for _ in range(rng.randint(3, 4)))
                 for _ in range(k)]
      strings = list(dict.fromkeys(strings))
      strings = [s for s in strings
                 if all(s == t or s not in t for t in strings)]
      if len(strings) < 2:
        continue
      result = kosaraju.superstring(strings)
      optimum = len(shortest_common_superstring.exact(
          ['#' + s for s in strings])) - 1
      self.assertLessEqual(len(result), bound(optimum),
                            f'strings={strings}, result={result}, '
                            f'optimum={optimum}')


if __name__ == '__main__':
  unittest.main()
