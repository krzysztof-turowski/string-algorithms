import numpy as np
import networkx as nx
from scipy.optimize import linear_sum_assignment

from common import prefix as _prefix

__all__ = [
    'get_overlap', 'get_distance', 'get_period', 'merge_path',
    'cycle_cover', 'max_weight_matching',
]


def get_overlap(s1, s2):
  return _prefix.get_overlap('#' + s1, '#' + s2)


def get_distance(s1, s2):
  return len(s1) - get_overlap(s1, s2)


def get_period(s):
  n = len(s)
  for p in range(1, n + 1):
    if all(s[i] == s[i + p] for i in range(n - p)):
      return p
  return n


def merge_path(path_indices, strings):
  if not path_indices:
    return ''
  res = strings[path_indices[0]]
  for i in range(1, len(path_indices)):
    u, v = strings[path_indices[i - 1]], strings[path_indices[i]]
    ov = get_overlap(u, v)
    res += v[ov:] if ov > 0 else v
  return res


def cycle_cover(weight_matrix, mode='min'):
  n = len(weight_matrix)
  if n == 1:
    return [[0]]
  matrix = np.array(weight_matrix, dtype=float)
  if mode == 'max':
    matrix = -matrix
  np.fill_diagonal(matrix, np.inf)
  row_ind, col_ind_raw = linear_sum_assignment(matrix)
  assignment = [0] * n
  for r, c in zip(row_ind, col_ind_raw):
    assignment[int(r)] = int(c)
  col_ind = assignment

  visited = [False] * n
  cycles = []
  for i in range(n):
    if not visited[i]:
      cycle, curr = [], i
      while not visited[curr]:
        visited[curr] = True
        cycle.append(curr)
        curr = col_ind[curr]
      cycles.append(cycle)
  return cycles


def max_weight_matching(weighted_edges):
  best = {}
  for (u, v), w in weighted_edges.items():
    key = frozenset((u, v))
    if key not in best or w > best[key]:
      best[key] = w

  graph = nx.Graph()
  for key, w in best.items():
    u, v = tuple(key)
    graph.add_edge(u, v, weight=w)

  return list(nx.max_weight_matching(graph, maxcardinality=True))
