import networkx as nx
import itertools

class PathColoringLemma:
    def __init__(self):
        pass

    # ==================== UTILITIES ====================

    def _reverse_graph(self, V_set, E_set):
        return set(V_set), set((v, u) for u, v in E_set)

    def _get_incident(self, node, E_subset):
        in_e = [e for e in E_subset if e[1] == node]
        out_e = [e for e in E_subset if e[0] == node]
        return in_e, out_e

    def _forms_disjoint_paths(self, edges):
        out_of, in_deg = {}, {}
        for u, v in edges:
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
        return visited == touched

    # ==================== A.1  ====================

    def _build_A1(self, edges):
        A1 = nx.Graph()
        A1.add_nodes_from(edges)
        edges_list = list(edges)
        for i in range(len(edges_list)):
            for j in range(i + 1, len(edges_list)):
                e, f = edges_list[i], edges_list[j]
                if e[1] == f[1] or e[0] == f[0]:
                    A1.add_edge(e, f)
        return A1

    def _partition_A_nodes(self, A1):
        Z, P, S = set(), set(), set()
        for comp in nx.connected_components(A1):
            if len(comp) == 1:
                S.update(comp)
            else:
                subgraph = A1.subgraph(comp)
                if all(d == 2 for n, d in subgraph.degree()):
                    Z.update(comp)
                else:
                    P.update(comp)
        return Z, P, S

    # ==================== A.2 ====================

    def _refine_A2(self, A1, Z, P, V_subset, E_subset):
        A2 = A1.copy()
        G_prime = nx.DiGraph()
        G_prime.add_nodes_from(V_subset)
        G_prime.add_edges_from(list(Z) + list(P))

        try:
            cycles = list(nx.simple_cycles(G_prime))
        except nx.NetworkXNoCycle:
            cycles = []

        for cycle_nodes in cycles:
            cycle_edges = []
            for i in range(len(cycle_nodes)):
                u, v = cycle_nodes[i], cycle_nodes[(i + 1) % len(cycle_nodes)]
                if (u, v) in Z or (u, v) in P:
                    cycle_edges.append((u, v))

            a_end_nodes = [e for e in cycle_edges if e in P and A2.degree(e) == 1]
            if len(a_end_nodes) >= 2:
                A2.add_edge(a_end_nodes[0], a_end_nodes[1])

        Z2, P2, S2 = self._partition_A_nodes(A2)
        return A2, Z2, P2, S2

    # ==================== A.3  ====================

    def _color_Z_P(self, A2, Z, P):
        visited = set()
        cols = {}
        for edge in Z.union(P):
            if edge not in visited:
                queue = [(edge, 0)]
                while queue:
                    curr, c = queue.pop(0)
                    if curr not in visited:
                        visited.add(curr)
                        cols[curr] = c
                        for neighbor in A2.neighbors(curr):
                            queue.append((neighbor, 1 - c))
        return cols

    def _build_full_B(self, S_edges, ZP_colors):
        B = nx.MultiDiGraph()
        B.add_nodes_from(S_edges)

        G0, G1 = nx.DiGraph(), nx.DiGraph()
        for edge, c in ZP_colors.items():
            if c == 0: G0.add_edge(*edge)
            elif c == 1: G1.add_edge(*edge)

        for e in S_edges:
            for f in S_edges:
                if e == f: continue
                he, tf = e[1], f[0]
                if he == tf:
                    B.add_edge(e, f, color=0)
                    B.add_edge(e, f, color=1)
                else:
                    if he in G0 and tf in G0 and nx.has_path(G0, he, tf):
                        B.add_edge(e, f, color=0)
                    if he in G1 and tf in G1 and nx.has_path(G1, he, tf):
                        B.add_edge(e, f, color=1)
        return B

    def _color_B_nodes(self, B):
        b_cols = {n: None for n in B.nodes()}

        cycles_0 = list(nx.simple_cycles(nx.DiGraph(((u, v) for u, v, d in B.edges(data=True) if d['color'] == 0))))
        cycles_1 = list(nx.simple_cycles(nx.DiGraph(((u, v) for u, v, d in B.edges(data=True) if d['color'] == 1))))
        all_mono_cycles = [(c, 0) for c in cycles_0] + [(c, 1) for c in cycles_1]

        while all_mono_cycles:
            active_cycles = []
            for cyc, c_col in all_mono_cycles:
                is_broken = False
                for n in cyc:
                    if b_cols[n] == 1 - c_col:
                        is_broken = True
                        break
                if not is_broken:
                    active_cycles.append((cyc, c_col))

            all_mono_cycles = active_cycles
            if not all_mono_cycles:
                break

            node_counts = {}
            for cyc, _ in all_mono_cycles:
                for n in cyc:
                    node_counts[n] = node_counts.get(n, 0) + 1

            free_node = None
            cycle_color = None
            for cyc, c_col in all_mono_cycles:
                for n in cyc:
                    if node_counts[n] == 1:
                        free_node = n
                        cycle_color = c_col
                        break
                if free_node: break

            if free_node:
                b_cols[free_node] = 1 - cycle_color
            else:
                node_to_cyc_idx = {}
                for i, (cyc, _) in enumerate(all_mono_cycles):
                    for n in cyc:
                        if n not in node_to_cyc_idx:
                            node_to_cyc_idx[n] = []
                        node_to_cyc_idx[n].append(i)

                b_star_adj = {i: [] for i in range(len(all_mono_cycles))}
                for a_node, cycles_sharing in node_to_cyc_idx.items():
                    if len(cycles_sharing) == 2:
                        u, v = cycles_sharing
                        b_star_adj[u].append((v, a_node))
                        b_star_adj[v].append((u, a_node))

                b_cycle_edges = None
                for u, neighbors in b_star_adj.items():
                    seen_to = {}
                    for v, edge_val in neighbors:
                        if v in seen_to:
                            b_cycle_edges = [seen_to[v], edge_val]
                            break
                        seen_to[v] = edge_val
                    if b_cycle_edges:
                        break

                if b_cycle_edges is None:
                    path_nodes = []
                    path_edges = []
                    visited = set()

                    def find_b_star_cycle(curr, parent_edge):
                        visited.add(curr)
                        path_nodes.append(curr)

                        for neighbor, edge_val in b_star_adj[curr]:
                            if parent_edge is not None and neighbor == parent_edge[0] and edge_val == parent_edge[1]:
                                continue
                            if neighbor in path_nodes:
                                start_idx = path_nodes.index(neighbor)
                                return path_edges[start_idx:] + [edge_val]
                            else:
                                path_edges.append(edge_val)
                                res = find_b_star_cycle(neighbor, (curr, edge_val))
                                if res: return res
                                path_edges.pop()

                        path_nodes.pop()
                        return None

                    b_cycle_edges = find_b_star_cycle(0, None)

                if b_cycle_edges:
                    for i, shared_a_node in enumerate(b_cycle_edges):
                        b_cols[shared_a_node] = i % 2
                else:
                    cyc, c_col = all_mono_cycles[0]
                    for i, n in enumerate(cyc):
                        if b_cols[n] is None: b_cols[n] = i % 2

        for n in B.nodes():
            if b_cols[n] is None:
                b_cols[n] = 0

        return b_cols

    # ==================== LEMMA 15 ====================

    def _lemma_15_inductive_coloring(self, current_V, current_E, forced_target_e=None, forced_cycle_nodes=None):
        colors = {}
        if len(current_V) <= 3:
            edges_list = list(current_E)

            for combo in itertools.product([0, 1], repeat=len(edges_list)):
                test_colors = {edges_list[i]: combo[i] for i in range(len(edges_list))}

                if all(self._forms_disjoint_paths(
                        [e for e, col in test_colors.items() if col == c])
                        for c in [0, 1]):
                    return test_colors

        A1 = self._build_A1(current_E)
        Z_init, P_init, S = self._partition_A_nodes(A1)
        A2, Z, P, S = self._refine_A2(A1, Z_init, P_init, current_V, current_E)

        for e in list(S):
            if e not in S: continue
            in_e, out_e = self._get_incident(e[0], current_E), self._get_incident(e[1], current_E)
            if len(in_e[0]) + len(in_e[1]) + len(out_e[0]) + len(out_e[1]) <= 2:
                colors[e] = 0
                S.remove(e)

        for e in list(S):
            if e not in S: continue

            f_next = next((f for f in S if e != f and e[1] == f[0]), None)
            if f_next:
                colors[e] = 0
                colors[f_next] = 1
                S.remove(e)
                S.remove(f_next)
                continue

            f_prev = next((f for f in S if e != f and e[0] == f[1]), None)
            if f_prev:
                colors[f_prev] = 0
                colors[e] = 1
                S.remove(e)
                S.remove(f_prev)

        T = set(S)

        G_prime = nx.DiGraph()
        G_prime.add_nodes_from(current_V)
        G_prime.add_edges_from(list(Z) + list(P))

        target_e = None
        cycle_nodes = None

        if forced_target_e and forced_target_e in T and forced_cycle_nodes:
            target_e = forced_target_e
            cycle_nodes = forced_cycle_nodes
        else:
            for t in sorted(list(T), key=str):
                if nx.has_path(G_prime, t[1], t[0]):
                    for p in nx.all_simple_paths(G_prime, t[1], t[0]):
                        f_cand = (p[-2], p[-1])
                        g_cand = (p[0], p[1])
                        if (f_cand in P and A2.degree(f_cand) == 1) or (g_cand in P and A2.degree(g_cand) == 1):
                            target_e = t
                            cycle_nodes = p
                            break
                if target_e: break

        if not target_e:
            zp_cols = self._color_Z_P(A2, Z, P)
            colors.update(zp_cols)
            B = self._build_full_B(list(S) + list(T), zp_cols)
            colors.update(self._color_B_nodes(B))
            return colors

        e = target_e
        x_node, y_node = e

        f_cyc = (cycle_nodes[-2], cycle_nodes[-1])
        g_cyc = (cycle_nodes[0], cycle_nodes[1])

        if f_cyc in P and A2.degree(f_cyc) == 1:
            f_1 = f_cyc
            g_1 = g_cyc
        else:
            rev_V, rev_E = self._reverse_graph(current_V, current_E)
            rev_e = (y_node, x_node)
            rev_cycle_nodes = list(reversed(cycle_nodes))
            rev_cols = self._lemma_15_inductive_coloring(rev_V, rev_E, forced_target_e=rev_e, forced_cycle_nodes=rev_cycle_nodes)
            for (u, v), col in rev_cols.items():
                colors[(v, u)] = col
            return colors

        in_x, out_x = self._get_incident(x_node, current_E)
        a_in = [x for x in in_x if x != f_1]
        a_out = [x for x in out_x if x != e]
        a_1 = a_in[0] if a_in else (a_out[0] if a_out else None)
        a_is_incoming = bool(a_in)

        _, out_y = self._get_incident(y_node, current_E)
        out_y_edges = [x for x in out_y if x != e]

        c_1 = next((x for x in out_y_edges if x != g_1), None)

        n_is_ge_1 = (g_1 in P and A2.degree(g_1) == 1)

        new_E = set(current_E) - {e, f_1}
        new_V = set(current_V) - {x_node}

        creates_2_cycle = False
        v_node = None
        new_a = None

        if a_1:
            if a_is_incoming:
                new_a = (a_1[0], y_node)
                if c_1 and new_a[0] == c_1[1]:
                    creates_2_cycle = True
                    v_node = new_a[0]
            else:
                new_a = (y_node, a_1[1])

        if not creates_2_cycle:
            if a_1:
                new_E.remove(a_1)
                new_E.add(new_a)

            sub_colors = self._lemma_15_inductive_coloring(new_V, new_E)
            colors.update(sub_colors)

            if a_1:
                col_a = colors.pop(new_a, 0)
                colors[a_1] = col_a
                colors[e] = col_a
                colors[f_1] = 1 - col_a
            else:
                colors[e] = 1 - colors.get(g_1, 0)
                z_node = f_1[0]
                out_z_sub = [edge for edge in new_E if edge[0] == z_node]
                colors[f_1] = 1 - colors[out_z_sub[0]] if out_z_sub else 1
        else:
            in_v, out_v = self._get_incident(v_node, current_E)
            h_edges = [x for x in in_v + out_v if x != a_1 and x != c_1]
            h = h_edges[0] if h_edges else None
            v_is_head_of_h = h and h[1] == v_node

            if not h or not v_is_head_of_h:
                in_z, _ = self._get_incident(f_1[0], current_E)
                b_edges = [x for x in in_z if x != g_1]
                b = b_edges[0] if b_edges else None

                if b != h or len(cycle_nodes) > 3:

                    if c_1 in new_E: new_E.remove(c_1)
                    if a_1 in new_E: new_E.remove(a_1)

                    mapped_edges = {}
                    double_edges_to_resolve = []

                    for edge in list(new_E):
                        if y_node in edge:
                            new_E.remove(edge)
                            mapped = (v_node if edge[0] == y_node else edge[0],
                                      v_node if edge[1] == y_node else edge[1])
                            if mapped in new_E:
                                double_edges_to_resolve.append((edge, mapped))
                            else:
                                new_E.add(mapped)
                                mapped_edges[mapped] = edge

                    new_V.discard(y_node)
                    sub_colors = self._lemma_15_inductive_coloring(new_V, new_E)
                    colors.update(sub_colors)

                    for mapped, orig in mapped_edges.items():
                        colors[orig] = colors.get(mapped, 0)
                    for orig, mapped in double_edges_to_resolve:
                        colors[orig] = 1 - colors.get(mapped, 0)
                    for mapped in mapped_edges:
                        if mapped in colors: del colors[mapped]

                    if c_1 is not None:
                        colors[c_1] = colors.get(h, 1 - colors.get(g_1, 0))
                    colors[a_1] = colors.get(g_1, 1 - colors.get(h, 0))
                    colors[e] = colors[a_1]
                    colors[f_1] = 1 - colors[e]
                else:
                    for key, val in {b: 1, c_1: 1, f_1: 1, a_1: 0, e: 0}.items():
                        if key is not None:
                            colors[key] = val
                    if g_1: colors[g_1] = 0

                    discarded = {b, c_1, f_1, a_1, e, g_1}
                    discarded = {x for x in discarded if x is not None}
                    new_E = set(current_E) - discarded
                    new_V = set(current_V)

                    sub_colors = self._lemma_15_inductive_coloring(new_V, new_E)
                    colors.update(sub_colors)

            else:
                if not n_is_ge_1:
                    if a_1: new_E.remove(a_1)
                    sub_colors = self._lemma_15_inductive_coloring(new_V, new_E)
                    colors.update(sub_colors)

                    c_col = colors.get(c_1, 0)
                    colors[a_1] = 1 - c_col
                    colors[e] = colors[a_1]
                    colors[f_1] = 1 - colors[e]
                else:
                    w1 = g_1[1]
                    w2 = h[0]
                    d = (w2, w1)

                    if w1 == w2:
                        discarded = {g_1, c_1, h, e, f_1, a_1}
                        new_E = set(current_E) - discarded
                        new_V = set(current_V) - {x_node, y_node, v_node}

                        sub_colors = self._lemma_15_inductive_coloring(new_V, new_E)
                        colors.update(sub_colors)

                        _, out_w1 = self._get_incident(w1, current_E)
                        g_2 = next((x for x in out_w1 if x not in discarded), None)

                        base_col = colors.get(g_2, 0) if g_2 else 0

                        colors[g_1] = 1 - base_col
                        colors[c_1] = base_col
                        colors[h]   = 1 - base_col
                        colors[a_1] = base_col
                        colors[e]   = 1 - base_col
                        colors[f_1] = 1 - base_col

                    else:
                        two_cycle_edge = next((x for x in new_E if x[0] == w1 and x[1] == w2), None)

                        if two_cycle_edge:
                            g_2 = (cycle_nodes[1], cycle_nodes[2])
                            g_3 = (cycle_nodes[2], cycle_nodes[3])

                            _, out_w1 = self._get_incident(cycle_nodes[1], current_E)
                            c_2 = next((x for x in out_w1 if x != g_2), None)

                            if two_cycle_edge == c_2:
                                discarded = {g_1, h, c_1, a_1, e, f_1}
                                discarded = {x for x in discarded if x is not None}
                                new_E = set(current_E) - discarded
                                new_V = set(current_V) - {x_node, y_node, v_node}

                                sub_colors = self._lemma_15_inductive_coloring(new_V, new_E)
                                colors.update(sub_colors)

                                w2_in, w2_out = self._get_incident(w2, current_E)
                                v_e = next((x for x in (w2_out + w2_in) if x != h and x != c_2), None)
                                C = colors.get(v_e, 0) if v_e else 0

                                colors[f_1] = C
                                colors[e]   = C
                                colors[g_1] = 1 - C
                                colors[h]   = 1 - C
                                colors[a_1] = 1 - C
                                colors[c_1] = C
                            else:
                                discarded = {two_cycle_edge, g_1, h, c_1, a_1, e, f_1}
                                discarded = {x for x in discarded if x is not None}

                                new_E = set(current_E) - discarded
                                new_V = set(current_V) - {x_node, y_node, v_node, w2}

                                mapped_edges = {}
                                double_edges_to_resolve = []
                                if g_3 and g_3 in new_E:
                                    new_E.remove(g_3)
                                    new_g3 = (w1, g_3[1])
                                    if new_g3 in new_E:
                                        double_edges_to_resolve.append((g_3, new_g3))
                                    else:
                                        new_E.add(new_g3)
                                        mapped_edges[new_g3] = g_3

                                sub_colors = self._lemma_15_inductive_coloring(new_V, new_E)
                                colors.update(sub_colors)

                                for mapped, orig in mapped_edges.items():
                                    colors[orig] = colors.pop(mapped, 0)
                                for orig, mapped in double_edges_to_resolve:
                                    colors[orig] = 1 - colors.get(mapped, 0)
                                for mapped in mapped_edges:
                                    if mapped in colors: del colors[mapped]

                                C = colors.get(g_3, 0) if g_3 else 0

                                if two_cycle_edge: colors[two_cycle_edge] = C
                                colors[g_1] = 1 - C
                                colors[c_1] = C
                                colors[h]   = 1 - C
                                colors[a_1] = 1 - C
                                colors[e]   = 1 - C
                                colors[f_1] = C
                        else:
                            discarded = {g_1, a_1, c_1, h, e, f_1}
                            new_E = (set(current_E) - discarded) | {d}
                            new_V = set(current_V) - {x_node, y_node, v_node}

                            sub_colors = self._lemma_15_inductive_coloring(new_V, new_E)
                            colors.update(sub_colors)

                            d_col = colors.pop(d, 0)
                            colors[g_1] = d_col
                            colors[a_1] = d_col
                            colors[h]   = d_col
                            colors[c_1] = 1 - d_col
                            colors[e]   = d_col
                            colors[f_1] = 1 - d_col

        return colors

    # ==================== COLORING ====================

    def color_graph(self, V, E):
        return self._lemma_15_inductive_coloring(set(V), set(E))
