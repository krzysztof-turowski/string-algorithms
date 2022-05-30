import enum
import itertools

import networkx

from common import prefix
from shortest_common_superstring.shortest_common_superstring import naive
from shortest_common_superstring.teng_yao import cycle_cover

VertexType = enum.IntEnum('VertexType', 'IN OUT HEAD TAIL JOIN')

def _cycle_edges(cycle):
  return zip(cycle, cycle[1:] + cycle[:1])

def _path_weight(matrix, cycle):
  return sum(matrix[i][j] for i, j in zip(cycle, cycle[1:]))

def max_weight_perfect_matching(edges):
  """Find maximum weight perfect matching.
  Input edges are given as list of triples (vertex, vertex, edge weight).
  Returns matching as set of pairs (vertex, vertex)."""
  graph = networkx.Graph()
  graph.add_weighted_edges_from(edges)
  return networkx.max_weight_matching(graph, maxcardinality=True)

def _half_edge_gadget(a, b, weight):
  """Half of gadget corresponding to a 2-cycle on vertices (a, b).
  Refer to Figures 1 and 2 in the original paper for explanation."""
  out_a, in_b = (VertexType.OUT, a), (VertexType.IN, b)
  head_ab, tail_ab = (VertexType.HEAD, a, b), (VertexType.TAIL, a, b)
  head_ba, join_ab = (VertexType.HEAD, b, a), (VertexType.JOIN, a, b)
  return [
    (out_a, tail_ab, weight),
    (tail_ab, head_ab, 0),
    (head_ab, in_b, weight),
    (join_ab, tail_ab, 0),
    (join_ab, head_ba, 0),
  ]

def _is_half_edge_matched(matching, a, b):
  """Check if either of half-edges (a, v(a,b)) or (v(a,b), b) is matched."""
  out_a, in_b = (VertexType.OUT, a), (VertexType.IN, b)
  head_ab, tail_ab = (VertexType.HEAD, a, b), (VertexType.TAIL, a, b)
  return (out_a, tail_ab) in matching or (in_b, head_ab) in matching or \
         (tail_ab, out_a) in matching or (head_ab, in_b) in matching

def max_cycle_cover_with_half_edges(matrix):
  """Find maximum weight cycle cover without 2-cycles but with half-edges.
  If both (u, v) and (v, u) is in returned set of edges,
  then the edge is undirected (it has two tails or two heads)."""
  n, auxiliary_graph = len(matrix), []
  for i, j in itertools.product(range(n), repeat = 2):
    if i != j:
      auxiliary_graph += _half_edge_gadget(i, j, matrix[i][j])
  matching = max_weight_perfect_matching(auxiliary_graph)
  cover = set()
  for i, j in itertools.product(range(n), repeat = 2):
    if i != j and _is_half_edge_matched(matching, i, j):
      cover.add((i, j))
  return cover

def _get_cycles(cover):
  """Iterate over weakly connected components of the cover,
  which are cycles if we ignore the edge direction."""
  neighbours, visited = {}, set()
  for i, j in cover:
    neighbours.setdefault(i, set())
    neighbours.setdefault(j, set())
    neighbours[i].add(j)
    neighbours[j].add(i)

  def next_on_cycle(previous, current):
    return next(v for v in neighbours[current] if v != previous)

  for v in neighbours:
    if v not in visited:
      cycle, previous, current = [v], v, next_on_cycle(-1, v)
      while current != v:
        cycle.append(current)
        previous, current = current, next_on_cycle(previous, current)
      visited.update(cycle)
      yield cycle

def _build_path_sets(cover, cycle):
  """Given a component of a cycle cover without 2-cycles but with half-edges,
  construct three sets of edges A, B, C, such that:
  - each edge set forms a node-disjoint path set on vertices of the component
  - total weight of all sets is equal to 2 times component weight
  """
  # Initial edge sets (forward+undirected, backward+undirected, directed).
  A = [e for e in _cycle_edges(cycle) if e in cover]
  B = [e for e in _cycle_edges(cycle[::-1]) if e in cover]
  C = [(u, v) for u, v in A + B if (v, u) not in cover]

  if len(A) < len(B):
    A, B = B, A

  # Handle special cases.
  if len(C) == len(cycle):
    # Cycle is directed.
    A, B, C = C[1:], C[:-1], [C[0], C[-1]]
  elif len(C) == 0:
    # Cycle is undirected. Move non-adjacent edges from A and B to C.
    edge_a = A[0]
    edge_b = next((u, v) for u, v in B if u not in edge_a and v not in edge_a)
    A.remove(edge_a)
    B.remove(edge_b)
    C += [edge_a, edge_b]
  elif len(A) == len(cycle):
    # Cycle contains single directed path. Move one edge from A to C.
    undirected_edge = next(e for e in A if e not in C)
    A.remove(undirected_edge)
    C.append(undirected_edge)

  return (A, B, C)

def _concatenate_path_set(edges, vertex_count):
  """Given a set of edges that form a node-disjoint path set,
  build ATSP path that contains all of them."""
  successors = dict(edges)
  vertices_with_predecessors = set(v for u, v in edges)
  tour = []
  for v in successors:
    if v not in vertices_with_predecessors:
      tour.append(v)
      while v in successors:
        v = successors[v]
        tour.append(v)
  tour.extend(set(range(vertex_count)) - set(tour))
  return tour

def _exact_max_atsp(matrix):
  return list(max(itertools.permutations(range(len(matrix))),
              key = lambda p: _path_weight(matrix, list(p))))

def approximate_max_atsp(matrix):
  """2/3-approximation of maximum weight ATSP path."""
  if len(matrix) < 3:
    return _exact_max_atsp(matrix)
  cover = max_cycle_cover_with_half_edges(matrix)
  path_sets = ([], [], [])
  for cycle in _get_cycles(cover):
    for path_set, to_add in zip(path_sets, _build_path_sets(cover, cycle)):
      path_set.extend(to_add)
  candidates = (_concatenate_path_set(p, len(matrix)) for p in path_sets)
  return max(candidates, key = lambda p: _path_weight(matrix, p))

def shortest_common_superstring(T):
  """5/2-approximation of shortest common superstring via reduction to ATSP."""
  representatives = []
  for cycle in cycle_cover(T):
    best = min((naive(cycle[i:] + cycle[:i]) for i in range(len(cycle))),
               key = len)
    representatives.append(best)
  matrix = [[prefix.get_overlap(w1, w2) for w2 in representatives]
            for w1 in representatives]
  best_order = approximate_max_atsp(matrix)
  return naive(list(representatives[j] for j in best_order))
