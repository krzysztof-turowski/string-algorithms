import itertools
from collections import defaultdict

import networkx

from . import common
from . import path_coloring


def _weight(weights, u, v):
    return weights.get((u, v), 0)


def _max_weight_cycle_cover(V, weights):
    V = list(V)
    n = len(V)
    matrix = [[_weight(weights, V[i], V[j]) if i != j else 0 for j in range(n)]
              for i in range(n)]
    index_cycles = common.cycle_cover(matrix, mode='max')
    cycles = []
    for index_cycle in index_cycles:
        vertices = [V[i] for i in index_cycle]
        L = len(vertices)
        cycles.append([(vertices[k], vertices[(k + 1) % L]) for k in range(L)])
    return cycles


def version_1(weights, C):
    P = []
    for cycle in C:
        lightest_edge = min(cycle, key=lambda edge: _weight(weights, *edge))
        for edge in cycle:
            if edge != lightest_edge:
                P.append(edge)
    return P


def version_2_real_variant(V, weights, C):
    contracted, real_two_cycles = _build_contracted_graph_for_version_2(
        V, weights, C)
    original_endpoint = {
        (u, v, key): data['original']
        for u, v, key, data in contracted.edges(keys=True, data=True)}

    final, reductions = _reduce_for_path_coloring(contracted)

    edge_of_pair = {(u, v): (u, v, key)
                    for u, v, key in final.edges(keys=True)}
    colors = {edge_of_pair[pair]: color for pair, color
              in path_coloring.color_graph(final.nodes(), edge_of_pair).items()}
    colors = _expand_reductions(colors, reductions)

    color_class_1 = [e for e, c in colors.items() if c == 0]
    color_class_2 = [e for e, c in colors.items() if c == 1]

    real_class_1 = [original_endpoint.get(e, e[:2]) for e in color_class_1]
    real_class_2 = [original_endpoint.get(e, e[:2]) for e in color_class_2]

    weight_1 = sum(_weight(weights, *e) for e in real_class_1)
    weight_2 = sum(_weight(weights, *e) for e in real_class_2)
    heavier_class = real_class_1 if weight_1 > weight_2 else real_class_2

    P = _uncontract_and_add_compatible_edges(
        weights, heavier_class, real_two_cycles)
    return P


def _build_contracted_graph_for_version_2(V, weights, C):
    G_prime_edges = {}
    three_plus_cycles = [cycle for cycle in C if len(cycle) >= 3]
    two_cycles = [cycle for cycle in C if len(cycle) == 2]

    real_two_cycles = []
    for cycle in two_cycles:
        edge_1, edge_2 = cycle[0], cycle[1]
        b_i = max(_weight(weights, *edge_1), _weight(weights, *edge_2))
        c_i = min(_weight(weights, *edge_1), _weight(weights, *edge_2))

        if b_i > 2 * c_i:
            three_plus_cycles.append(cycle)
        else:
            real_two_cycles.append(cycle)
            u, v = edge_1[0], edge_1[1]
            G_prime_edges[(u, v)] = 2 * (b_i - c_i)

    for u in V:
        for v in V:
            if (u != v and (u, v) not in G_prime_edges
                    and (v, u) not in G_prime_edges):
                G_prime_edges[(u, v)] = max(_weight(weights, u, v),
                                            _weight(weights, v, u))

    M = common.max_weight_matching(G_prime_edges)

    directed_edges = _get_directed_counterparts(weights, M)
    for cycle in three_plus_cycles:
        lightest_edge = min(cycle, key=lambda edge: _weight(weights, *edge))
        directed_edges.extend([e for e in cycle if e != lightest_edge])

    contracted = _contract_2_cycles(V, directed_edges, real_two_cycles)
    return contracted, real_two_cycles


def _contract_2_cycles(V, edges, two_cycles):
    parent = {v: v for v in V}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    for cycle in two_cycles:
        union(cycle[0][0], cycle[0][1])

    groups = {}
    for v in V:
        groups.setdefault(find(v), []).append(v)

    representative = {}
    super_nodes = set()
    for i, (root, members) in enumerate(groups.items()):
        if len(members) == 1:
            representative[members[0]] = members[0]
            super_nodes.add(members[0])
        else:
            super_id = f"S_{i}"
            for m in members:
                representative[m] = super_id
            super_nodes.add(super_id)

    contracted = networkx.MultiDiGraph()
    contracted.add_nodes_from(super_nodes)
    for u, v in edges:
        representative_u = representative[u]
        representative_v = representative[v]
        if representative_u != representative_v:
            contracted.add_edge(representative_u, representative_v,
                                original=(u, v))

    return contracted


def _get_directed_counterparts(weights, M):
    directed_edges = []
    for (u, v) in M:
        if _weight(weights, u, v) >= _weight(weights, v, u):
            directed_edges.append((u, v))
        else:
            directed_edges.append((v, u))
    return directed_edges


def _contract_induced_2_cycle(graph, two_cycle):
    u, v = two_cycle
    edge_1 = (u, v, next(iter(graph[u][v])))
    edge_2 = (v, u, next(iter(graph[v][u])))

    candidates = []
    for mid_edge, other_edge in [(edge_1, edge_2), (edge_2, edge_1)]:
        m0, m1 = mid_edge[0], mid_edge[1]
        in_m0 = [e for e in graph.in_edges(m0, keys=True) if e != other_edge]
        out_m1 = [e for e in graph.out_edges(m1, keys=True) if e != other_edge]
        x_edge = in_m0[0] if in_m0 else None
        y_edge = out_m1[0] if out_m1 else None
        if x_edge and y_edge and x_edge[0] == y_edge[1]:
            continue
        candidates.append((mid_edge, other_edge, m0, m1, x_edge, y_edge))

    if not candidates:
        raise RuntimeError(
            f'cannot eliminate induced 2-cycle {edge_1} and {edge_2}')

    candidates.sort(key=lambda c: 0 if (c[4] or c[5]) else 1)
    mid_edge, other_edge, m0, m1, x_edge, y_edge = candidates[0]

    chain = (([x_edge] if x_edge else []) + [mid_edge]
             + ([y_edge] if y_edge else []))
    for edge in chain + [other_edge]:
        graph.remove_edge(*edge)

    if x_edge and y_edge:
        tail, head = x_edge[0], y_edge[1]
        new_edge = (tail, head, graph.add_edge(tail, head))
        graph.remove_nodes_from([m0, m1])
    elif x_edge:
        new_edge = (x_edge[0], m1, graph.add_edge(x_edge[0], m1))
        graph.remove_node(m0)
    elif y_edge:
        new_edge = (m0, y_edge[1], graph.add_edge(m0, y_edge[1]))
        graph.remove_node(m1)
    else:
        graph.remove_nodes_from([m0, m1])
        return None, chain, other_edge, {mid_edge: 0, other_edge: 1}

    return new_edge, chain, other_edge, None


def _reduce_for_path_coloring(graph):
    graph = graph.copy()
    reductions = []
    while True:
        parallel = next(((u, v) for u, v in graph.edges()
                         if graph.number_of_edges(u, v) > 1), None)
        if parallel is not None:
            reductions.append((_expand_parallel_elimination,
                               _contract_parallel_edges(graph, parallel)))
            continue

        two_cycle = next(((u, v) for u, v in graph.edges()
                          if graph.has_edge(v, u)), None)
        if two_cycle is not None:
            reductions.append((_expand_induced_elimination,
                               _contract_induced_2_cycle(graph, two_cycle)))
            continue

        return graph, reductions


def _expand_reductions(colors, reductions):
    for expand, record in reversed(reductions):
        expand(colors, record)
    return colors


def _contract_parallel_edges(graph, parallel):
    u, v = parallel
    copies = [(u, v, key) for key in graph[u][v]]
    a_edge, = graph.in_edges(u, keys=True) or (None,)
    b_edge, = graph.out_edges(v, keys=True) or (None,)

    merged = f'P_{u}_{v}'
    graph.add_node(merged)
    new_a = new_b = None
    if a_edge is not None:
        graph.remove_edge(*a_edge)
        new_a = (a_edge[0], merged, graph.add_edge(a_edge[0], merged))
    if b_edge is not None:
        graph.remove_edge(*b_edge)
        new_b = (merged, b_edge[1], graph.add_edge(merged, b_edge[1]))
    graph.remove_nodes_from([u, v])

    return copies, a_edge, b_edge, new_a, new_b


def _expand_parallel_elimination(colors, record):
    copies, a_edge, b_edge, new_a, new_b = record
    if a_edge is not None:
        colors[a_edge] = colors.pop(new_a, 0)
    if b_edge is not None:
        colors[b_edge] = colors.pop(new_b, 0)
    colors[copies[0]] = 0
    colors[copies[1]] = 1


def _expand_induced_elimination(colors, record):
    new_edge, chain, other_edge, fixed = record
    if fixed is not None:
        colors.update(fixed)
        return
    c = colors.pop(new_edge, 0)
    for e in chain:
        colors[e] = c
    colors[other_edge] = 1 - c


def _uncontract_and_add_compatible_edges(weights, color_class_edges,
                                         two_cycles):
    P = list(color_class_edges)

    in_degree = defaultdict(int)
    out_degree = defaultdict(int)
    for u, v in P:
        out_degree[u] += 1
        in_degree[v] += 1

    for cycle in two_cycles:
        edge_1, edge_2 = cycle[0], cycle[1]
        can_add_edge_1 = (out_degree[edge_1[0]] == 0
                          and in_degree[edge_1[1]] == 0)
        can_add_edge_2 = (out_degree[edge_2[0]] == 0
                          and in_degree[edge_2[1]] == 0)

        weight_1 = _weight(weights, *edge_1)
        weight_2 = _weight(weights, *edge_2)

        chosen = None
        if can_add_edge_1 and can_add_edge_2:
            chosen = edge_1 if weight_1 > weight_2 else edge_2
        elif can_add_edge_1:
            chosen = edge_1
        elif can_add_edge_2:
            chosen = edge_2

        if chosen:
            P.append(chosen)
            out_degree[chosen[0]] += 1
            in_degree[chosen[1]] += 1

    return P


def version_3_real_variant(E, weights, C):
    E = set(E)
    x = 7
    C_prime = []

    for cycle in C:
        if len(cycle) > x:
            C_prime.extend(_break_cycle_into_pieces(weights, cycle, x))
        else:
            C_prime.append(cycle)

    vertex_to_piece = {}
    for index, piece in enumerate(C_prime):
        for u, v in piece:
            vertex_to_piece[u] = index
            vertex_to_piece[v] = index

    weight_cache = {}

    def cached_compatible_weight(target_node, piece_index, is_tail):
        key = (piece_index, target_node, is_tail)
        if key not in weight_cache:
            weight_cache[key] = _compatible_weight(
                E, weights, target_node, C_prime[piece_index],
                is_tail=is_tail, is_head=not is_tail)
        return weight_cache[key]

    G_prime_E = {}
    original_edges_map = {}

    for e in E:
        u, v = e[0], e[1]
        tail_piece_index = vertex_to_piece.get(u)
        head_piece_index = vertex_to_piece.get(v)

        if (tail_piece_index is not None and head_piece_index is not None
                and tail_piece_index != head_piece_index):
            compatible_weight_tail = cached_compatible_weight(
                u, tail_piece_index, is_tail=True)
            compatible_weight_head = cached_compatible_weight(
                v, head_piece_index, is_tail=False)

            w_prime = (_weight(weights, u, v) + compatible_weight_tail
                       + compatible_weight_head)

            if w_prime > G_prime_E.get(
                    (tail_piece_index, head_piece_index), -1):
                G_prime_E[(tail_piece_index, head_piece_index)] = w_prime
                original_edges_map[(tail_piece_index, head_piece_index)] = e

    M_prime = common.max_weight_matching(G_prime_E)

    P = _reconstruct_paths_from_matching(
        E, weights, M_prime, C_prime, original_edges_map)
    return P


def _break_cycle_into_pieces(weights, cycle, x):
    L = len(cycle)
    k = -(-L // x)
    if k <= 1:
        return [cycle]

    base, extra = divmod(L - k, k)

    best_pieces = None
    best_cut_weight = None
    for start in range(L):
        pieces, i, cut_weight = [], start, 0
        for j in range(k):
            size = base + (1 if j < extra else 0)
            if size > 0:
                pieces.append([cycle[(i + t) % L] for t in range(size)])
            cut_weight += _weight(weights, *cycle[(i + size) % L])
            i += size + 1
        if best_cut_weight is None or cut_weight < best_cut_weight:
            best_cut_weight = cut_weight
            best_pieces = pieces

    return best_pieces


def _compatible_weight(E, weights, target_node, piece,
                       is_tail=False, is_head=False):
    hamiltonian_path = _compute_compatible_hamiltonian_path(
        E, weights, piece, target_node, is_tail, is_head)
    return sum(_weight(weights, *edge) for edge in hamiltonian_path)


def _compute_compatible_hamiltonian_path(E, weights, piece, target_node=None,
                                         is_tail=False, is_head=False):
    V_piece = set()
    for u, v in piece:
        V_piece.add(u)
        V_piece.add(v)

    best_path = []
    best_weight = -1

    for permutation in itertools.permutations(V_piece):
        if is_tail and permutation[-1] != target_node: continue
        if is_head and permutation[0] != target_node: continue

        current_path = []
        current_weight = 0
        valid = True
        for i in range(len(permutation) - 1):
            u, v = permutation[i], permutation[i+1]
            if (u, v) not in E:
                valid = False
                break
            current_path.append((u, v))
            current_weight += _weight(weights, u, v)

        if valid and current_weight > best_weight:
            best_weight = current_weight
            best_path = current_path

    return best_path


def _reconstruct_paths_from_matching(E, weights, M_prime, C_prime,
                                     original_edges_map):
    P = []
    matched_cycles = set()

    for u_index, v_index in M_prime:
        matched_cycles.add(u_index)
        matched_cycles.add(v_index)

        e = (original_edges_map.get((u_index, v_index))
             or original_edges_map.get((v_index, u_index)))
        if not e: continue

        P.append(e)

        P.extend(_compute_compatible_hamiltonian_path(
            E, weights, C_prime[u_index], e[0], is_tail=True))
        P.extend(_compute_compatible_hamiltonian_path(
            E, weights, C_prime[v_index], e[1], is_head=True))

    for i, piece in enumerate(C_prime):
        if i not in matched_cycles:
            P.extend(_compute_compatible_hamiltonian_path(E, weights, piece))

    return P


def _patch_paths_to_tour(V, P):
    out_of = {u: v for u, v in P}
    in_of = {v: u for u, v in P}

    chains = []
    visited = set()
    for start in V:
        if start in visited or start in in_of:
            continue
        chain = [start]
        visited.add(start)
        while chain[-1] in out_of:
            next_node = out_of[chain[-1]]
            chain.append(next_node)
            visited.add(next_node)
        chains.append(chain)

    tour = list(P)
    for i in range(len(chains)):
        end_of_this = chains[i][-1]
        start_of_next = chains[(i + 1) % len(chains)][0]
        tour.append((end_of_this, start_of_next))

    return tour


_DUMMY_VERTEX = 'dummy'


def max_tsp_tour(V, E, weights, versions=(1, 2, 3)):
    versions = tuple(versions)
    if not versions or any(v not in (1, 2, 3) for v in versions):
        raise ValueError(
            f'versions must be a non-empty subset of {{1, 2, 3}}, '
            f'got {versions}')

    V = list(V)
    if len(V) % 2:
        return _tour_through_dummy_vertex(V, E, weights, versions)
    return _best_tour(V, E, weights, versions)


def _tour_through_dummy_vertex(V, E, weights, versions):
    padded_V = V + [_DUMMY_VERTEX]
    padded_E = (list(E) + [(v, _DUMMY_VERTEX) for v in V]
                + [(_DUMMY_VERTEX, v) for v in V])
    padded_weights = dict(weights)
    for v in V:
        padded_weights[(v, _DUMMY_VERTEX)] = 0
        padded_weights[(_DUMMY_VERTEX, v)] = 0

    tour = _best_tour(padded_V, padded_E, padded_weights, versions)

    into_dummy = next(u for u, v in tour if v == _DUMMY_VERTEX)
    out_of_dummy = next(v for u, v in tour if u == _DUMMY_VERTEX)
    return ([edge for edge in tour if _DUMMY_VERTEX not in edge]
            + [(into_dummy, out_of_dummy)])


def _best_tour(V, E, weights, versions):
    C = _max_weight_cycle_cover(V, weights)

    tours = []
    for version in versions:
        if version == 1:
            P = version_1(weights, C)
        elif version == 2:
            P = version_2_real_variant(V, weights, C)
        else:
            P = version_3_real_variant(E, weights, C)
        tours.append(_patch_paths_to_tour(V, P))

    return max(tours, key=lambda t: sum(_weight(weights, u, v) for u, v in t))


def _hamiltonian_path_indices(path_edges):
    out_of = {u: v for u, v in path_edges}
    in_of = {v: u for u, v in path_edges}
    vertices = set(out_of) | set(in_of)
    start = next(v for v in vertices if v not in in_of)
    path = [start]
    while path[-1] in out_of:
        path.append(out_of[path[-1]])
    return path


def superstring(strings, versions=(1, 2, 3)):
    if not strings:
        return ''
    if len(strings) == 1:
        return strings[0]

    n = len(strings)
    V = list(range(n))
    E = [(i, j) for i in V for j in V if i != j]
    weights = {(i, j): common.get_overlap(strings[i], strings[j]) for i, j in E}

    tour = max_tsp_tour(V, E, weights, versions=versions)
    lightest_edge = min(tour, key=lambda edge: weights.get(edge, 0))
    path_edges = [e for e in tour if e != lightest_edge]
    path_indices = _hamiltonian_path_indices(path_edges)
    return common.merge_path(path_indices, strings)
