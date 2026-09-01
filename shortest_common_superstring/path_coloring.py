import networkx
import itertools


def _forms_disjoint_paths(edges):
    graph = networkx.DiGraph()
    graph.add_edges_from(edges)
    return (all(degree <= 1 for _, degree in graph.in_degree())
            and all(degree <= 1 for _, degree in graph.out_degree())
            and networkx.is_directed_acyclic_graph(graph))

def _build_A1(edges):
    A1 = networkx.Graph()
    A1.add_nodes_from(edges)
    edges_list = list(edges)
    for i in range(len(edges_list)):
        for j in range(i + 1, len(edges_list)):
            e, f = edges_list[i], edges_list[j]
            if e[1] == f[1] or e[0] == f[0]:
                A1.add_edge(e, f)
    return A1

def _partition_A_nodes(A1):
    Z, P, S = set(), set(), set()
    for component in networkx.connected_components(A1):
        if len(component) == 1:
            S.update(component)
        else:
            subgraph = A1.subgraph(component)
            if all(degree == 2 for _, degree in subgraph.degree()):
                Z.update(component)
            else:
                P.update(component)
    return Z, P, S

def _refine_A2(A1, Z, P, V_subset, E_subset):
    A2 = A1.copy()
    G_prime = networkx.DiGraph()
    G_prime.add_nodes_from(V_subset)
    G_prime.add_edges_from(list(Z) + list(P))

    try:
        cycles = list(networkx.simple_cycles(G_prime))
    except networkx.NetworkXNoCycle:
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

    Z2, P2, S2 = _partition_A_nodes(A2)
    return A2, Z2, P2, S2

def _color_Z_P(A2, Z, P):
    visited = set()
    colors = {}
    for edge in Z.union(P):
        if edge not in visited:
            queue = [(edge, 0)]
            while queue:
                current, color = queue.pop(0)
                if current not in visited:
                    visited.add(current)
                    colors[current] = color
                    for neighbor in A2.neighbors(current):
                        queue.append((neighbor, 1 - color))
    return colors

def _build_full_B(S_edges, ZP_colors):
    B = networkx.MultiDiGraph()
    B.add_nodes_from(S_edges)

    reachable = {}
    for color in (0, 1):
        monochromatic = networkx.DiGraph()
        monochromatic.add_edges_from(
            edge for edge, edge_color in ZP_colors.items()
            if edge_color == color)
        reachable[color] = networkx.transitive_closure_dag(monochromatic)

    for e in S_edges:
        for f in S_edges:
            if e == f: continue
            head_of_e, tail_of_f = e[1], f[0]
            if head_of_e == tail_of_f:
                B.add_edge(e, f, color=0)
                B.add_edge(e, f, color=1)
            else:
                for color in (0, 1):
                    if reachable[color].has_edge(head_of_e, tail_of_f):
                        B.add_edge(e, f, color=color)
    return B

def _color_B_nodes(B):
    b_colors = {node: None for node in B.nodes()}

    cycles_0 = list(networkx.simple_cycles(networkx.DiGraph(
        ((u, v) for u, v, data in B.edges(data=True) if data['color'] == 0))))
    cycles_1 = list(networkx.simple_cycles(networkx.DiGraph(
        ((u, v) for u, v, data in B.edges(data=True) if data['color'] == 1))))
    all_monochromatic_cycles = ([(cycle, 0) for cycle in cycles_0]
                                + [(cycle, 1) for cycle in cycles_1])

    while all_monochromatic_cycles:
        active_cycles = []
        for cycle, cycle_color in all_monochromatic_cycles:
            is_broken = False
            for node in cycle:
                if b_colors[node] == 1 - cycle_color:
                    is_broken = True
                    break
            if not is_broken:
                active_cycles.append((cycle, cycle_color))

        all_monochromatic_cycles = active_cycles
        if not all_monochromatic_cycles:
            break

        node_counts = {}
        for cycle, _ in all_monochromatic_cycles:
            for node in cycle:
                node_counts[node] = node_counts.get(node, 0) + 1

        free_node = None
        free_node_cycle_color = None
        for cycle, cycle_color in all_monochromatic_cycles:
            for node in cycle:
                if node_counts[node] == 1:
                    free_node = node
                    free_node_cycle_color = cycle_color
                    break
            if free_node: break

        if free_node:
            b_colors[free_node] = 1 - free_node_cycle_color
        else:
            node_to_cycle_indices = {}
            for i, (cycle, _) in enumerate(all_monochromatic_cycles):
                for node in cycle:
                    if node not in node_to_cycle_indices:
                        node_to_cycle_indices[node] = []
                    node_to_cycle_indices[node].append(i)

            b_star_adjacency = {
                i: [] for i in range(len(all_monochromatic_cycles))}
            for a_node, cycles_sharing in node_to_cycle_indices.items():
                if len(cycles_sharing) == 2:
                    u, v = cycles_sharing
                    b_star_adjacency[u].append((v, a_node))
                    b_star_adjacency[v].append((u, a_node))

            b_cycle_edges = None
            for u, neighbors in b_star_adjacency.items():
                seen_to = {}
                for v, edge_value in neighbors:
                    if v in seen_to:
                        b_cycle_edges = [seen_to[v], edge_value]
                        break
                    seen_to[v] = edge_value
                if b_cycle_edges:
                    break

            if b_cycle_edges is None:
                path_nodes = []
                path_edges = []
                visited = set()

                def find_b_star_cycle(current, parent_edge):
                    visited.add(current)
                    path_nodes.append(current)

                    for neighbor, edge_value in b_star_adjacency[current]:
                        if (parent_edge is not None
                                and neighbor == parent_edge[0]
                                and edge_value == parent_edge[1]):
                            continue
                        if neighbor in path_nodes:
                            start_index = path_nodes.index(neighbor)
                            return path_edges[start_index:] + [edge_value]
                        else:
                            path_edges.append(edge_value)
                            result = find_b_star_cycle(
                                neighbor, (current, edge_value))
                            if result: return result
                            path_edges.pop()

                    path_nodes.pop()
                    return None

                b_cycle_edges = find_b_star_cycle(0, None)

            if b_cycle_edges:
                for i, shared_a_node in enumerate(b_cycle_edges):
                    b_colors[shared_a_node] = i % 2
            else:
                cycle, cycle_color = all_monochromatic_cycles[0]
                for i, node in enumerate(cycle):
                    if b_colors[node] is None: b_colors[node] = i % 2

    for node in B.nodes():
        if b_colors[node] is None:
            b_colors[node] = 0

    return b_colors

def _lemma_15_inductive_coloring(current_V, current_E,
                                 forced_target_e=None,
                                 forced_cycle_nodes=None):
    colors = {}
    if len(current_V) <= 3:
        edges_list = list(current_E)

        for combination in itertools.product([0, 1], repeat=len(edges_list)):
            test_colors = {edges_list[i]: combination[i]
                           for i in range(len(edges_list))}

            if all(_forms_disjoint_paths(
                    [e for e, edge_color in test_colors.items()
                     if edge_color == color])
                    for color in [0, 1]):
                return test_colors

    G = networkx.DiGraph()
    G.add_nodes_from(current_V)
    G.add_edges_from(current_E)

    A1 = _build_A1(current_E)
    Z_init, P_init, S = _partition_A_nodes(A1)
    A2, Z, P, S = _refine_A2(A1, Z_init, P_init, current_V, current_E)

    for e in list(S):
        if e not in S: continue
        if G.degree(e[0]) + G.degree(e[1]) <= 2:
            colors[e] = 0
            S.remove(e)

    for e in list(S):
        if e not in S: continue

        if f_next := next((f for f in S if e != f and e[1] == f[0]), None):
            colors[e] = 0
            colors[f_next] = 1
            S.remove(e)
            S.remove(f_next)
            continue

        if f_previous := next((f for f in S if e != f and e[0] == f[1]), None):
            colors[f_previous] = 0
            colors[e] = 1
            S.remove(e)
            S.remove(f_previous)

    T = set(S)

    G_prime = networkx.DiGraph()
    G_prime.add_nodes_from(current_V)
    G_prime.add_edges_from(list(Z) + list(P))

    target_e = None
    cycle_nodes = None

    if forced_target_e and forced_target_e in T and forced_cycle_nodes:
        target_e = forced_target_e
        cycle_nodes = forced_cycle_nodes
    else:
        for t in sorted(list(T), key=str):
            if networkx.has_path(G_prime, t[1], t[0]):
                target_e = t
                cycle_nodes = next(
                    networkx.all_simple_paths(G_prime, t[1], t[0]))
                break

    if not target_e:
        zp_cols = _color_Z_P(A2, Z, P)
        colors.update(zp_cols)
        B = _build_full_B(list(S) + list(T), zp_cols)
        colors.update(_color_B_nodes(B))
        return colors

    e = target_e
    x_node, y_node = e

    f_cycle = (cycle_nodes[-2], cycle_nodes[-1])
    g_cycle = (cycle_nodes[0], cycle_nodes[1])

    if f_cycle in P and A2.degree(f_cycle) == 1:
        f_1 = f_cycle
        g_1 = g_cycle
    else:
        reversed_G = G.reverse(copy=False)
        reversed_V = set(reversed_G.nodes())
        reversed_E = set(reversed_G.edges())
        reversed_e = (y_node, x_node)
        reversed_cycle_nodes = list(reversed(cycle_nodes))
        reversed_colors = _lemma_15_inductive_coloring(
            reversed_V, reversed_E, forced_target_e=reversed_e,
            forced_cycle_nodes=reversed_cycle_nodes)
        for (u, v), col in reversed_colors.items():
            colors[(v, u)] = col
        return colors

    x_in_edges = list(G.in_edges(x_node))
    x_out_edges = list(G.out_edges(x_node))
    a_incoming = [x for x in x_in_edges if x != f_1]
    a_outgoing = [x for x in x_out_edges if x != e]
    if a_incoming:
        a_1 = a_incoming[0]
    else:
        a_1 = a_outgoing[0] if a_outgoing else None
    a_is_incoming = bool(a_incoming)

    y_out_edges = list(G.out_edges(y_node))
    out_y_edges = [x for x in y_out_edges if x != e]

    c_1 = next((x for x in out_y_edges if x != g_1), None)

    n_is_at_least_one = (g_1 in P and A2.degree(g_1) == 1)

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

        subproblem_colors = _lemma_15_inductive_coloring(new_V, new_E)
        colors.update(subproblem_colors)

        if a_1:
            color_a = colors.pop(new_a, 0)
            colors[a_1] = color_a
            colors[e] = color_a
            colors[f_1] = 1 - color_a
        else:
            colors[e] = 1 - colors.get(g_1, 0)
            z_node = f_1[0]
            z_out_edges = [edge for edge in new_E if edge[0] == z_node]
            colors[f_1] = 1 - colors[z_out_edges[0]] if z_out_edges else 1
    else:
        v_in_edges = list(G.in_edges(v_node))
        v_out_edges = list(G.out_edges(v_node))
        h_edges = [x for x in v_in_edges + v_out_edges if x != a_1 and x != c_1]
        h = h_edges[0] if h_edges else None
        v_is_head_of_h = h and h[1] == v_node

        if not h or not v_is_head_of_h:
            z_in_edges = list(G.in_edges(f_1[0]))
            b_edges = [x for x in z_in_edges if x != g_1]
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
                subproblem_colors = _lemma_15_inductive_coloring(new_V, new_E)
                colors.update(subproblem_colors)

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

                subproblem_colors = _lemma_15_inductive_coloring(new_V, new_E)
                colors.update(subproblem_colors)

        else:
            if not n_is_at_least_one:
                if a_1: new_E.remove(a_1)
                subproblem_colors = _lemma_15_inductive_coloring(new_V, new_E)
                colors.update(subproblem_colors)

                c_1_color = colors.get(c_1, 0)
                colors[a_1] = 1 - c_1_color
                colors[e] = colors[a_1]
                colors[f_1] = 1 - colors[e]
            else:
                w_1 = g_1[1]
                w_2 = h[0]
                d = (w_2, w_1)

                if w_1 == w_2:
                    discarded = {g_1, c_1, h, e, f_1, a_1}
                    new_E = set(current_E) - discarded
                    new_V = set(current_V) - {x_node, y_node, v_node}

                    subproblem_colors = _lemma_15_inductive_coloring(
                        new_V, new_E)
                    colors.update(subproblem_colors)

                    w_1_out_edges = list(G.out_edges(w_1))
                    g_2 = next(
                        (x for x in w_1_out_edges
                         if x not in discarded), None)

                    base_color = colors.get(g_2, 0) if g_2 else 0

                    colors[g_1] = 1 - base_color
                    colors[c_1] = base_color
                    colors[h]   = 1 - base_color
                    colors[a_1] = base_color
                    colors[e]   = 1 - base_color
                    colors[f_1] = 1 - base_color

                else:
                    two_cycle_edge = next(
                        (x for x in new_E
                         if x[0] == w_1 and x[1] == w_2), None)

                    if two_cycle_edge:
                        g_2 = (cycle_nodes[1], cycle_nodes[2])
                        g_3 = (cycle_nodes[2], cycle_nodes[3])

                        w_1_out_edges = list(G.out_edges(cycle_nodes[1]))
                        c_2 = next((x for x in w_1_out_edges if x != g_2), None)

                        if two_cycle_edge == c_2:
                            discarded = {g_1, h, c_1, a_1, e, f_1}
                            discarded = {x for x in discarded if x is not None}
                            new_E = set(current_E) - discarded
                            new_V = set(current_V) - {x_node, y_node, v_node}

                            subproblem_colors = _lemma_15_inductive_coloring(
                        new_V, new_E)
                            colors.update(subproblem_colors)

                            w_2_in_edges = list(G.in_edges(w_2))
                            w_2_out_edges = list(G.out_edges(w_2))
                            v_e = next(
                                (x for x in (w_2_out_edges + w_2_in_edges)
                                 if x != h and x != c_2), None)
                            C = colors.get(v_e, 0) if v_e else 0

                            colors[f_1] = C
                            colors[e]   = C
                            colors[g_1] = 1 - C
                            colors[h]   = 1 - C
                            colors[a_1] = 1 - C
                            colors[c_1] = C
                        else:
                            discarded = {two_cycle_edge, g_1, h, c_1,
                                         a_1, e, f_1}
                            discarded = {x for x in discarded if x is not None}

                            new_E = set(current_E) - discarded
                            new_V = (set(current_V)
                                     - {x_node, y_node, v_node, w_2})

                            mapped_edges = {}
                            double_edges_to_resolve = []
                            if g_3 and g_3 in new_E:
                                new_E.remove(g_3)
                                new_g3 = (w_1, g_3[1])
                                if new_g3 in new_E:
                                    double_edges_to_resolve.append(
                                        (g_3, new_g3))
                                else:
                                    new_E.add(new_g3)
                                    mapped_edges[new_g3] = g_3

                            subproblem_colors = _lemma_15_inductive_coloring(
                        new_V, new_E)
                            colors.update(subproblem_colors)

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

                        subproblem_colors = _lemma_15_inductive_coloring(
                        new_V, new_E)
                        colors.update(subproblem_colors)

                        d_color = colors.pop(d, 0)
                        colors[g_1] = d_color
                        colors[a_1] = d_color
                        colors[h]   = d_color
                        colors[c_1] = 1 - d_color
                        colors[e]   = d_color
                        colors[f_1] = 1 - d_color

    return colors

def color_graph(V, E):
    edges = list(E)
    if len(edges) != len(set(edges)):
        raise ValueError(
            'the path coloring lemma needs a graph without parallel edges')
    return _lemma_15_inductive_coloring(set(V), set(edges))
