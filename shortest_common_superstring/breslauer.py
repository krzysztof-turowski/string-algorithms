from lyndon import critical_factorization as _critical_factorization

from . import kosaraju
from .common import (get_overlap, get_distance, get_period, merge_path,
                     cycle_cover)

def get_cycle_cover(strings):
    n = len(strings)
    dist_matrix = [[get_distance(strings[i], strings[j]) if i != j else 0
                    for j in range(n)] for i in range(n)]
    return cycle_cover(dist_matrix, mode='min'), dist_matrix


def _critical_split(w):
    index, _ = _critical_factorization.constant_space('#' + w, len(w))
    return w[:index - 1], w[index - 1:]


def get_omega_rotation(W):
    L = len(W)
    if L <= 1:
        return W

    x, y = _critical_split(W)
    w = y + x

    u, v = _critical_split(w)
    if len(u) <= L / 2:
        return w
    return v + u

def build_broken_cycle_string(sequence, strings):
    res = ""
    for i in range(len(sequence) - 1):
        u = strings[sequence[i]]
        v = strings[sequence[i+1]]
        ov = get_overlap(u, v)
        res += u[:-ov] if ov > 0 else u
    res += strings[sequence[-1]]
    return res

def construct_tc(cycle_indices, strings):
    L = len(cycle_indices)
    if L == 1:
        return strings[cycle_indices[0]]
        
    W = ""
    for i in range(L):
        u = strings[cycle_indices[i]]
        v = strings[cycle_indices[(i + 1) % L]]
        ov = get_overlap(u, v)
        W += u[:-ov] if ov > 0 else u
    omega = get_omega_rotation(W)
    
    broken_strings = []
    for break_point in range(L):
        seq = [cycle_indices[(break_point + i) % L] for i in range(L)]
        broken_strings.append(build_broken_cycle_string(seq, strings))
        
    max_broken_length = max(len(h) for h in broken_strings)
    search_space = omega * ((max_broken_length // len(omega)) + 3)
    
    # TODO O(L * |search_space|), one scan per broken string.
    # Aho-Corasick would be (|search_space| + sum of their lengths).
    earliest_start = float('inf')
    earliest_H = ""
    for H_j in broken_strings:
        idx = search_space.find(H_j)
        if idx != -1 and idx < earliest_start:
            earliest_start = idx
            earliest_H = H_j
            
    end_idx = earliest_start + len(earliest_H)
    return search_space[:end_idx]


def remove_substrings(strings):
    clean_set = []
    sorted_strings = sorted(strings, key=len, reverse=True)
    
    for s in sorted_strings:
        is_substring = False
        for clean_s in clean_set:
            if s in clean_s:
                is_substring = True
                break
        
        if not is_substring:
            clean_set.append(s)
            
    return clean_set

def breslauer_jiang_jiang_simple(strings):
    if not strings:
        return ""
    strings = [s[1:] if s.startswith('#') else s for s in strings]
    strings = remove_substrings(strings)

    if len(strings) == 1:
        return '#' + strings[0]

    C, _ = get_cycle_cover(strings)

    T = []
    for c in C:
        tc = construct_tc(c, strings)
        T.append(tc)

    CC, _ = get_cycle_cover(T)

    broken_paths = []
    for cycle in CC:
        if len(cycle) == 1:
            broken_paths.append(T[cycle[0]])
            continue

        break_index = 0
        for i in range(len(cycle)):
            u_idx = cycle[i]
            v_idx = cycle[(i + 1) % len(cycle)]
            if get_period(T[u_idx]) <= get_period(T[v_idx]):
                break_index = i
                break

        path_indices = [cycle[(break_index + i) % len(cycle)]
                        for i in range(1, len(cycle) + 1)]
        broken_paths.append(merge_path(path_indices, T))

    final_superstring = '#' + ''.join(broken_paths)
    return final_superstring

def breslauer_jiang_jiang_by_overlap(strings,
                                     overlap_algorithm=kosaraju.superstring):
    if not strings:
        return ""
    strings = [s[1:] if s.startswith('#') else s for s in strings]
    strings = remove_substrings(strings)

    if len(strings) == 1:
        return '#' + strings[0]

    C, _ = get_cycle_cover(strings)

    T = []
    for c in C:
        tc = construct_tc(c, strings)
        T.append(tc)
    final_superstring = "#" + overlap_algorithm(T)
    return final_superstring
    