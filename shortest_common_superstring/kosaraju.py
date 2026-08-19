import itertools
from collections import defaultdict

from . import common
from . import path_coloring

class DirectedMaxTSPApproximation:
    def __init__(self, V, E, weights):
        self.V = V
        self.E = set(E)
        self.weights = weights

    def w(self, u, v):
        return self.weights.get((u, v), 0)

    # ==================== VERSION 1 ====================

    def version_1(self, C):
        P = []
        for cycle in C:
            lightest_edge = min(cycle, key=lambda edge: self.w(*edge))
            for edge in cycle:
                if edge != lightest_edge:
                    P.append(edge)
        return P

    # ==================== VERSION 2 ====================

    def version_2_real_variant(self, C):
        contracted_V, contracted_E, real_two_cycles, original_endpoint = \
            self.build_contracted_graph_for_version_2(C)

        final_V, final_E, eliminations = self._eliminate_induced_2_cycles(contracted_V, contracted_E)

        colors = path_coloring.PathColoringLemma().color_graph(set(final_V), set(final_E))
        colors = self._expand_induced_eliminations(colors, eliminations)

        color_class_1 = [e for e, c in colors.items() if c == 0]
        color_class_2 = [e for e, c in colors.items() if c == 1]

        real_class_1 = [original_endpoint.get(e, e) for e in color_class_1]
        real_class_2 = [original_endpoint.get(e, e) for e in color_class_2]

        w1 = sum(self.w(*e) for e in real_class_1)
        w2 = sum(self.w(*e) for e in real_class_2)
        heavier_class = real_class_1 if w1 > w2 else real_class_2

        P = self.uncontract_and_add_compatible_edges(heavier_class, real_two_cycles)
        return P

    def build_contracted_graph_for_version_2(self, C):
        G_prime_edges = {}
        three_plus_cycles = [cycle for cycle in C if len(cycle) >= 3]
        two_cycles = [cycle for cycle in C if len(cycle) == 2]

        real_two_cycles = []
        for cycle in two_cycles:
            e1, e2 = cycle[0], cycle[1]
            b_i = max(self.w(*e1), self.w(*e2))
            c_i = min(self.w(*e1), self.w(*e2))

            if b_i > 2 * c_i:
                three_plus_cycles.append(cycle)
            else:
                real_two_cycles.append(cycle)
                u, v = e1[0], e1[1]
                G_prime_edges[(u, v)] = 2 * (b_i - c_i)

        for u in self.V:
            for v in self.V:
                if u != v and (u, v) not in G_prime_edges and (v, u) not in G_prime_edges:
                    G_prime_edges[(u, v)] = max(self.w(u, v), self.w(v, u))

        M = self.compute_max_weight_matching(G_prime_edges)

        directed_edges = self.get_directed_counterparts(M)
        for cycle in three_plus_cycles:
            lightest_edge = min(cycle, key=lambda edge: self.w(*edge))
            directed_edges.extend([e for e in cycle if e != lightest_edge])

        contracted_V, contracted_E, original_endpoint = \
            self.contract_2_cycles(directed_edges, real_two_cycles)
        return contracted_V, contracted_E, real_two_cycles, original_endpoint

    def contract_2_cycles(self, edges, two_cycles):
        parent = {v: v for v in self.V}

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
        for v in self.V:
            groups.setdefault(find(v), []).append(v)

        rep = {}
        super_nodes = set()
        for i, (root, members) in enumerate(groups.items()):
            if len(members) == 1:
                rep[members[0]] = members[0]
                super_nodes.add(members[0])
            else:
                super_id = f"S_{i}"
                for m in members:
                    rep[m] = super_id
                super_nodes.add(super_id)

        contracted_E = []
        original_endpoint = {}
        for u, v in edges:
            r_u, r_v = rep[u], rep[v]
            if r_u != r_v:
                contracted_edge = (r_u, r_v)
                contracted_E.append(contracted_edge)
                original_endpoint[contracted_edge] = (u, v)

        return list(super_nodes), contracted_E, original_endpoint

    def get_directed_counterparts(self, M):
        directed_edges = []
        for (u, v) in M:
            if self.w(u, v) >= self.w(v, u):
                directed_edges.append((u, v))
            else:
                directed_edges.append((v, u))
        return directed_edges

    def _eliminate_induced_2_cycles(self, V, E):
        V, E = set(V), set(E)
        eliminations = []

        while True:
            pair_edges = {}
            for e in E:
                pair_edges.setdefault(frozenset(e), []).append(e)
            cycle_pair = next((es for es in pair_edges.values() if len(es) == 2), None)
            if cycle_pair is None:
                return V, E, eliminations

            e1, e2 = cycle_pair
            candidates = []
            for mid_edge, other_edge in [(e1, e2), (e2, e1)]:
                m0, m1 = mid_edge
                in_m0 = [e for e in E if e[1] == m0 and e != other_edge]
                out_m1 = [e for e in E if e[0] == m1 and e != other_edge]
                x_edge = in_m0[0] if in_m0 else None
                y_edge = out_m1[0] if out_m1 else None
                if x_edge and y_edge and x_edge[0] == y_edge[1]:
                    continue
                candidates.append((mid_edge, other_edge, m0, m1, x_edge, y_edge))

            if not candidates:
                raise RuntimeError(
                    f'Nie można wyeliminować indukowanego 2-cyklu {tuple(cycle_pair)}: E={E}')

            candidates.sort(key=lambda c: 0 if (c[4] or c[5]) else 1)
            mid_edge, other_edge, m0, m1, x_edge, y_edge = candidates[0]

            chain = ([x_edge] if x_edge else []) + [mid_edge] + ([y_edge] if y_edge else [])
            E -= set(chain) | {other_edge}

            if x_edge and y_edge:
                new_edge = (x_edge[0], y_edge[1])
                E.add(new_edge)
                V -= {m0, m1}
                eliminations.append((new_edge, chain, other_edge, None))
            elif x_edge:
                new_edge = (x_edge[0], m1)
                E.add(new_edge)
                V.discard(m0)
                eliminations.append((new_edge, chain, other_edge, None))
            elif y_edge:
                new_edge = (m0, y_edge[1])
                E.add(new_edge)
                V.discard(m1)
                eliminations.append((new_edge, chain, other_edge, None))
            else:
                V -= {m0, m1}
                eliminations.append((None, chain, other_edge, {mid_edge: 0, other_edge: 1}))

    def _expand_induced_eliminations(self, colors, eliminations):
        for new_edge, chain, other_edge, fixed in reversed(eliminations):
            if fixed is not None:
                colors.update(fixed)
                continue
            c = colors.pop(new_edge, 0)
            for e in chain:
                colors[e] = c
            colors[other_edge] = 1 - c
        return colors

    def uncontract_and_add_compatible_edges(self, color_class_edges, two_cycles):
        P = list(color_class_edges)

        in_deg = defaultdict(int)
        out_deg = defaultdict(int)
        for u, v in P:
            out_deg[u] += 1
            in_deg[v] += 1

        for cycle in two_cycles:
            e1, e2 = cycle[0], cycle[1]
            can_add_e1 = (out_deg[e1[0]] == 0 and in_deg[e1[1]] == 0)
            can_add_e2 = (out_deg[e2[0]] == 0 and in_deg[e2[1]] == 0)

            w1, w2 = self.w(*e1), self.w(*e2)

            chosen = None
            if can_add_e1 and can_add_e2:
                chosen = e1 if w1 > w2 else e2
            elif can_add_e1:
                chosen = e1
            elif can_add_e2:
                chosen = e2

            if chosen:
                P.append(chosen)
                out_deg[chosen[0]] += 1
                in_deg[chosen[1]] += 1

        return P

    # ==================== VERSION 3 ====================

    def version_3_real_variant(self, C):
        x = 7
        C_prime = []

        for cycle in C:
            if len(cycle) > x:
                C_prime.extend(self.break_cycle_into_pieces(cycle, x))
            else:
                C_prime.append(cycle)

        vertex_to_piece = {}
        for idx, piece in enumerate(C_prime):
            for u, v in piece:
                vertex_to_piece[u] = idx
                vertex_to_piece[v] = idx

        weight_cache = {}

        def cached_compatible_weight(target_node, piece_idx, is_tail):
            key = (piece_idx, target_node, is_tail)
            if key not in weight_cache:
                e_arg = (target_node, None) if is_tail else (None, target_node)
                weight_cache[key] = self.compatible_weight(
                    e_arg, C_prime[piece_idx], is_tail=is_tail, is_head=not is_tail)
            return weight_cache[key]

        G_prime_E = {}
        original_edges_map = {}

        for e in self.E:
            u, v = e[0], e[1]
            c_tail_idx = vertex_to_piece.get(u)
            c_head_idx = vertex_to_piece.get(v)

            if c_tail_idx is not None and c_head_idx is not None and c_tail_idx != c_head_idx:
                cw_tail = cached_compatible_weight(u, c_tail_idx, is_tail=True)
                cw_head = cached_compatible_weight(v, c_head_idx, is_tail=False)

                w_prime = self.w(u, v) + cw_tail + cw_head

                if w_prime > G_prime_E.get((c_tail_idx, c_head_idx), -1):
                    G_prime_E[(c_tail_idx, c_head_idx)] = w_prime
                    original_edges_map[(c_tail_idx, c_head_idx)] = e

        M_prime = self.compute_max_weight_matching(G_prime_E)

        P = self.reconstruct_paths_from_matching(M_prime, C_prime, original_edges_map)
        return P

    def break_cycle_into_pieces(self, cycle, x):
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
                cut_weight += self.w(*cycle[(i + size) % L])
                i += size + 1
            if best_cut_weight is None or cut_weight < best_cut_weight:
                best_cut_weight = cut_weight
                best_pieces = pieces

        return best_pieces

    def compatible_weight(self, e, piece, is_tail=False, is_head=False):
        H_path = self.compute_compatible_hamiltonian_path(piece, e, is_tail, is_head)
        return sum(self.w(*edge) for edge in H_path)

    def compute_compatible_hamiltonian_path(self, piece, e=None, is_tail=False, is_head=False):
        V_piece = set()
        for u, v in piece:
            V_piece.add(u)
            V_piece.add(v)

        target_node = e[0] if is_tail else (e[1] if is_head else None)

        best_path = []
        best_weight = -1

        for perm in itertools.permutations(V_piece):
            if is_tail and perm[-1] != target_node: continue
            if is_head and perm[0] != target_node: continue

            current_path = []
            current_weight = 0
            valid = True
            for i in range(len(perm) - 1):
                u, v = perm[i], perm[i+1]
                if (u, v) not in self.E:
                    valid = False
                    break
                current_path.append((u, v))
                current_weight += self.w(u, v)

            if valid and current_weight > best_weight:
                best_weight = current_weight
                best_path = current_path

        return best_path

    def reconstruct_paths_from_matching(self, M_prime, C_prime, original_edges_map):
        P = []
        matched_cycles = set()

        for u_idx, v_idx in M_prime:
            matched_cycles.add(u_idx)
            matched_cycles.add(v_idx)

            e = original_edges_map.get((u_idx, v_idx))
            if not e:
                e = original_edges_map.get((v_idx, u_idx))
            if not e: continue

            P.append(e)

            P.extend(self.compute_compatible_hamiltonian_path(C_prime[u_idx], e, is_tail=True))
            P.extend(self.compute_compatible_hamiltonian_path(C_prime[v_idx], e, is_head=True))

        for i, piece in enumerate(C_prime):
            if i not in matched_cycles:
                P.extend(self.compute_compatible_hamiltonian_path(piece))

        return P

    def run(self, versions=(1, 2, 3)):
        versions = tuple(versions)
        if not versions or any(v not in (1, 2, 3) for v in versions):
            raise ValueError(f'versions must be a non-empty subset of {{1, 2, 3}}, got {versions}')

        C = self.compute_max_weight_cycle_cover()

        tours = []
        for v in versions:
            if v == 1:
                P = self.version_1(C)
            elif v == 2:
                P = self.version_2_real_variant(C)
            else:
                P = self.version_3_real_variant(C)
            tours.append(self.patch_paths_to_tour(P))

        return max(tours, key=lambda t: sum(self.w(u, v) for u, v in t))

    def compute_max_weight_cycle_cover(self):
        V = list(self.V)
        n = len(V)
        matrix = [[self.w(V[i], V[j]) if i != j else 0 for j in range(n)]
                  for i in range(n)]
        index_cycles = common.cycle_cover(matrix, mode='max')
        cycles = []
        for index_cycle in index_cycles:
            vertices = [V[i] for i in index_cycle]
            L = len(vertices)
            cycles.append([(vertices[k], vertices[(k + 1) % L]) for k in range(L)])
        return cycles

    def compute_max_weight_matching(self, edges):
        return common.max_weight_matching(edges)

    def patch_paths_to_tour(self, P):
        out_of = {u: v for u, v in P}
        in_of = {v: u for u, v in P}

        chains = []
        visited = set()
        for start in self.V:
            if start in visited or start in in_of:
                continue
            chain = [start]
            visited.add(start)
            while chain[-1] in out_of:
                nxt = out_of[chain[-1]]
                chain.append(nxt)
                visited.add(nxt)
            chains.append(chain)

        tour = list(P)
        for i in range(len(chains)):
            end_of_this = chains[i][-1]
            start_of_next = chains[(i + 1) % len(chains)][0]
            tour.append((end_of_this, start_of_next))

        return tour


# ==================== SUPERSTRING ====================

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

    tour = DirectedMaxTSPApproximation(V, E, weights).run(versions=versions)
    lightest_edge = min(tour, key=lambda edge: weights.get(edge, 0))
    path_edges = [e for e in tour if e != lightest_edge]
    path_indices = _hamiltonian_path_indices(path_edges)
    return common.merge_path(path_indices, strings)
