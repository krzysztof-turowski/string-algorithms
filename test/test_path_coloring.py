import os
import random
import sys
import unittest

import parameterized

from shortest_common_superstring import path_coloring

HANDMADE_GRAPHS = [
    [
        'transitive_tournament',
        [1, 2, 3],
        [(1, 2), (2, 3), (1, 3)],
    ],
    [
        'trivial_isolated_edges',
        [1, 2, 3, 4, 5, 6],
        [(1, 2), (3, 4), (4, 5)],
    ],
    [
        'connected_components_induction',
        [1, 2, 3, 4, 5, 6],
        [(1, 2), (2, 3), (3, 1), (4, 5), (5, 6), (6, 4), (1, 4), (2, 5)],
    ],
    [
        'nested_cycles_bottleneck',
        [0, 1, 2, 3, 4],
        [(0, 3), (0, 1), (1, 4), (2, 1), (2, 0), (3, 2), (4, 3)],
    ],
    [
        'dense_degree_three',
        [0, 2, 3, 4],
        [(0, 3), (0, 4), (2, 0), (3, 4), (3, 2), (4, 2)],
    ],
    [
        'hex_weave',
        [0, 1, 2, 3, 4, 5],
        [(0, 3), (0, 2), (1, 5), (2, 4), (2, 3), (3, 1), (4, 1), (5, 4),
         (5, 0)],
    ],
    [
        'gordian_knot',
        [0, 1, 2, 3, 4, 5, 6],
        [(0, 4), (1, 2), (1, 0), (2, 5), (3, 6), (3, 2), (4, 1), (5, 3),
         (5, 6), (6, 4)],
    ],
    [
        'asymmetric_cycles_with_source',
        [0, 1, 2, 3, 4, 5],
        [(0, 1), (1, 5), (1, 4), (2, 5), (3, 0), (4, 3), (4, 0), (5, 3)],
    ],
    [
        'dense_core_with_external_source',
        [0, 1, 2, 3, 4, 5],
        [(0, 3), (1, 2), (1, 0), (2, 0), (2, 5), (3, 1), (4, 5), (5, 3)],
    ],
    [
        'multiple_interleaved_cycles',
        [0, 1, 2, 3, 4, 5, 6],
        [(0, 1), (1, 3), (1, 2), (2, 5), (2, 6), (3, 0), (4, 0), (5, 4),
         (5, 6), (6, 3)],
    ],
    [
        'regression_none_key_isolated_component',
        [0, 1, 2, 3],
        [(0, 2), (3, 1), (1, 2), (3, 0), (2, 3)],
    ],
    [
        'regression_b_star_double_edge',
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [(5, 4), (0, 3), (1, 4), (6, 7), (1, 3), (5, 7), (3, 8), (4, 8),
         (0, 1), (7, 0), (8, 6), (6, 5)],
    ],
]


BRANCH_LINES = {
    351: 'no_2cycle_created/a_1_present',
    356: 'no_2cycle_created/a_1_none',
    385: 'tail_or_no_h/general_contraction (Fig. A.5)',
    418: 'tail_or_no_h/isolated_component_b_eq_h (Fig. A.6)',
    427: 'head_of_h/simple_not_n_ge_1',
    450: 'head_of_h/w1_eq_w2_loop (Fig. A.9)',
    486: 'head_of_h/two_cycle_edge_eq_c2 (Fig. A.10, "c3==h")',
    495: 'head_of_h/two_cycle_edge_neq_c2 (Fig. A.10, "c3!=h")',
    548: 'head_of_h/general_d_case (Fig. A.11)',
}

CASE_CASCADE_GRAPHS = [
    [
        'fig_A5_general_contraction',
        [0, 1, 2, 3, 4],
        [(1, 2), (0, 4), (0, 2), (3, 0), (4, 3), (2, 3)],
    ],
    [
        'fig_A6_isolated_component_b_eq_h',
        [0, 1, 2, 3],
        [(3, 0), (0, 2), (3, 1), (1, 2), (2, 3)],
    ],
    [
        'head_of_h_simple_not_n_ge_1',
        [0, 1, 2, 3, 4],
        [(4, 0), (1, 4), (2, 4), (1, 3), (3, 0), (2, 3), (0, 2)],
    ],
    [
        'fig_A9_w1_eq_w2_loop',
        [0, 1, 2, 3, 4],
        [(1, 0), (2, 0), (3, 1), (4, 3), (3, 2), (4, 2), (0, 4)],
    ],
    [
        'fig_A10_two_cycle_edge_eq_c2',
        [0, 1, 2, 3, 4, 5],
        [(4, 2), (0, 1), (2, 0), (1, 4), (3, 5), (1, 3), (0, 5), (5, 2)],
    ],
    [
        'fig_A10_two_cycle_edge_neq_c2_USER_IMAGE_CASE',
        [0, 1, 2, 3, 4, 5],
        [(1, 5), (4, 0), (2, 4), (4, 3), (0, 1), (0, 5), (1, 3), (5, 2),
         (3, 2)],
    ],
    [
        'fig_A11_general_d_case',
        [0, 1, 2, 3, 4],
        [(3, 0), (4, 1), (4, 3), (1, 0), (2, 1), (0, 4)],
    ],
    [
        'fig_A5_general_contraction_shortest_path',
        [0, 1, 2, 3, 4],
        [(2, 1), (3, 2), (0, 4), (0, 3), (1, 3), (2, 0)],
    ],
    [
        'fig_A10_two_cycle_edge_neq_c2_shortest_path',
        [0, 1, 2, 3, 4, 5, 6],
        [(2, 1), (1, 4), (3, 4), (0, 6), (2, 3), (5, 0), (1, 0), (6, 5),
         (4, 6), (5, 2)],
    ],
    [
        'no_2cycle_created_a_1_present',
        [0, 1, 2, 3],
        [(2, 3), (1, 2), (3, 0), (1, 0), (0, 2)],
    ],
    [
        'no_2cycle_created_a_1_none',
        [0, 1, 2, 3],
        [(1, 3), (2, 3), (2, 1), (1, 0), (0, 2)],
    ],
]


def verify_coloring(V, E, colors):
  if len(colors) != len(E):
    return False
  for c in [0, 1]:
    out_of, in_deg = {}, {}
    for u, v, *_ in (e for e, col in colors.items() if col == c):
      if u in out_of:
        return False
      out_of[u] = v
      in_deg[v] = in_deg.get(v, 0) + 1
      if in_deg[v] > 1:
        return False
    touched = set(out_of) | set(in_deg)
    visited = set()
    for start in (u for u in touched if u not in in_deg):
      curr = start
      while True:
        if curr in visited:
          return False
        visited.add(curr)
        if curr not in out_of:
          break
        curr = out_of[curr]
    if visited != touched:
      return False
  return True


def generate_random_valid_graph(n_nodes, p_edge=0.01):
  adjacency = {v: set() for v in range(n_nodes)}
  reverse_adjacency = {v: set() for v in range(n_nodes)}
  edges = []
  potential_edges = [(u, v) for u in range(n_nodes)
                     for v in range(n_nodes) if u != v]
  random.shuffle(potential_edges)
  for u, v in potential_edges:
    if random.random() > p_edge:
      continue
    if v in adjacency[u] or u in adjacency[v]:
      continue
    if (len(adjacency[u]) + len(reverse_adjacency[u]) >= 3
        or len(adjacency[v]) + len(reverse_adjacency[v]) >= 3
        or len(adjacency[u]) >= 2 or len(reverse_adjacency[v]) >= 2):
      continue
    adjacency[u].add(v)
    reverse_adjacency[v].add(u)
    edges.append((u, v))
  return list(range(n_nodes)), edges


class TestPathColoring(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_path_coloring(self, V, E):
    colors = path_coloring.color_graph(V, E)
    self.assertTrue(verify_coloring(V, E, colors),
                    f'V={V}, E={E}, colors={colors}')

  @parameterized.parameterized.expand(HANDMADE_GRAPHS)
  def test_handmade_examples(self, _, V, E):
    self.check_path_coloring(V, E)

  @parameterized.parameterized.expand(CASE_CASCADE_GRAPHS)
  def test_case_cascade_examples(self, _, V, E):
    self.check_path_coloring(V, E)

  def test_case_cascade_branch_coverage(self):
    hit_lines = set()

    def tracer(frame, event, arg):
      if (event == 'line'
          and frame.f_code.co_name == '_lemma_15_inductive_coloring'):
        if frame.f_lineno in BRANCH_LINES:
          hit_lines.add(frame.f_lineno)
      return tracer

    sys.settrace(tracer)
    try:
      for _, V, E in CASE_CASCADE_GRAPHS:
        path_coloring.color_graph(V, E)
    finally:
      sys.settrace(None)

    missing = {BRANCH_LINES[l] for l in BRANCH_LINES if l not in hit_lines}
    self.assertFalse(
        missing,
        f'Lemma 15 case-cascade branches never hit: {missing}. '
        'Marker line numbers in BRANCH_LINES may have shifted after a change '
        'in path_coloring.py, or a branch actually became unreachable -- '
        'check both.')

  @run_large
  def test_case_cascade_branch_coverage_random_fuzz(self):
    hit_lines = set()

    def tracer(frame, event, arg):
      if (event == 'line'
          and frame.f_code.co_name == '_lemma_15_inductive_coloring'):
        if frame.f_lineno in BRANCH_LINES:
          hit_lines.add(frame.f_lineno)
      return tracer

    sys.settrace(tracer)
    try:
      for _ in range(20000):
        n = random.randint(4, 9)
        p = random.choice([0.6, 0.7, 0.8, 0.9, 1.0])
        V, E = generate_random_valid_graph(n, p_edge=p)
        if not E:
          continue
        colors = path_coloring.color_graph(V, E)
        self.assertTrue(verify_coloring(V, E, colors),
                        f'V={V}, E={E}, colors={colors}')
    finally:
      sys.settrace(None)

    missing = {BRANCH_LINES[l] for l in BRANCH_LINES if l not in hit_lines}
    self.assertFalse(missing,
                     f'Branches never hit by random fuzzing: {missing}')

  def test_small_random(self):
    tests, n_low, n_high = 200, 4, 12
    for _ in range(tests):
      n = random.randint(n_low, n_high)
      V, E = generate_random_valid_graph(n, p_edge=0.2)
      self.check_path_coloring(V, E)

  @run_large
  def test_large_random(self):
    tests, n_low, n_high = 1000, 90, 100
    for _ in range(tests):
      n = random.randint(n_low, n_high)
      V, E = generate_random_valid_graph(n)
      self.check_path_coloring(V, E)


if __name__ == '__main__':
  unittest.main()
