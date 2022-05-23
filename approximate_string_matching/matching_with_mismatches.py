import math
import collections

from approximate_string_matching import distance
from string_indexing import suffix_tree
from common import prefix, lca


def naive_edit_distance(t, w, n, m, k):
  D = distance.distance_row(
      w, t, m, n, distance.EDIT_DISTANCE, distance.FirstRow.ZEROS)
  for i, v in enumerate(D[1:]):
    if v <= k:
      yield i + 1

def _next_possible_occurence(t, n, m, k, BM_k, BAD, j):
  while j <= n + k:
    r, i, bad, d = j, m, 0, m
    while i > k >= bad:
      if i >= m - k and r <= n:
        d = min(d, BM_k[(i, t[r])])
      if r <= n and BAD[(i, t[r])]:
        bad += 1
      i, r = i - 1, r - 1
    if bad <= k and j <= n + k:
      npo = j - m - k
      j += max(k + 1, d)
      return npo, j
    j += max(k + 1, d)
  return n + 1, j

def _boyer_moore_bad_environment(p, m, k, A):
  bad_table = {(i, a): True for i in range(1, m + 1) for a in A}
  for i in range(1, m + 1):
    for j in range(max(0, i - k), min(i + k, m) + 1):
      bad_table[(j, p[i])] = False
  return bad_table

def _boyer_moore_shift(p, m, k, A):
  ready = {a: m + 1 for a in A}
  BM_k = {(i, a): m for a in A for i in range(m, m - k - 1, -1)}
  for i in range(m - 1, 0, -1):
    for j in range(ready[p[i]] - 1, max(i, m - k) - 1, -1):
      BM_k[(j, p[i])] = j - i
    ready[p[i]] = max(i, m - k)
  return BM_k

# pylint: disable=too-many-locals
def approximate_boyer_moore(t, p, n, m, k):
  A = set(list(t[1:] + p[1:]))
  BM_k = _boyer_moore_shift(p, m, k, A)
  BAD = _boyer_moore_bad_environment(p, m, k, A)

  j, top, D_0 = m, min(k + 1, m), list(range(m + 1))
  current, j = _next_possible_occurence(t, n, m, k, BM_k, BAD, j)
  current = max(current, 1)
  D, last = D_0[:], current + m + 2 * k

  while current <= n:
    for r in range(current, last + 1):
      c = 0
      for i in range(1, top + 1):
        d = (c if r <= n and p[i] == t[r] else min(D[i - 1], D[i], c) + 1)
        c, D[i] = D[i], d
      while D[top] > k:
        top -= 1
      if top == m:
        if r <= n:
          yield r
      else:
        top += 1
    next_possible, j = _next_possible_occurence(t, n, m, k, BM_k, BAD, j)
    if next_possible > last + 1:
      D, top, current = D_0[:], min(k + 1, m), next_possible
    else:
      current = last + 1
    last = next_possible + m + 2 * k

def naive_hamming(t, w, n, m, k):
  for i in range(1, n - m + 2):
    if distance.hamming_distance('#' + t[i:i + m], w, m, m) <= k:
      yield i

def _compute_pattern(
    t, w, k, length, b_frst_mm_p, last, PAT_M, TEXT_M, is_pattern):

  def _extend_pattern(cur_p, frst_p, found_mm):
    frst_p = max(frst_p, cur_p) + 1
    while(found_mm < k + 1 and (frst_p - cur_p <= length)
          and not (is_pattern and frst_p >= len(w))):
      if t[frst_p] != w[frst_p-cur_p]:
        found_mm += 1
        TEXT_M[cur_p][found_mm] = frst_p - cur_p
      frst_p += 1
    return frst_p - 1

  def _merge_pattern(cur_p, b_frst_mm_p, frst_p):
    t_it, p_it, no_mm = 0, 1, 0
    for x in range(1, k + 3):
      if b_frst_mm_p + TEXT_M[b_frst_mm_p][x] > cur_p :
        t_it = x
        break

    w_slide = cur_p - b_frst_mm_p
    while not(no_mm == k+1 or t_it == k+2 or
              (cur_p + PAT_M[w_slide][p_it]>frst_p
               and TEXT_M[b_frst_mm_p][t_it] == len(w))):
      if (cur_p + PAT_M[w_slide][p_it] >
          b_frst_mm_p + TEXT_M[b_frst_mm_p][t_it]):
        no_mm += 1
        TEXT_M[cur_p][no_mm] = TEXT_M[b_frst_mm_p][t_it] - w_slide
        t_it += 1
      elif (cur_p + PAT_M[w_slide][p_it] <
            b_frst_mm_p + TEXT_M[b_frst_mm_p][t_it]):
        no_mm += 1
        TEXT_M[cur_p][no_mm] = PAT_M[cur_p - b_frst_mm_p][p_it]
        p_it += 1
      else:
        if w[PAT_M[w_slide][p_it]] != t[cur_p+PAT_M[w_slide][p_it]]:
          no_mm +=1
          TEXT_M[cur_p][no_mm] = PAT_M[w_slide][p_it]
        p_it +=1
        t_it +=1
    return no_mm

  frst_p = b_frst_mm_p
  for cur_p in range(b_frst_mm_p, last):
    if is_pattern:
      frst_p = min(frst_p, len(w) - 1)
    found_mm = _merge_pattern(
        cur_p, b_frst_mm_p, frst_p) if cur_p < frst_p else 0
    if found_mm < k + 1:
      b_frst_mm_p = 1 if is_pattern else cur_p
      frst_p = _extend_pattern(cur_p, frst_p, found_mm)

def _pattern_matching(w: str, k: int, m: int):
  PAT_M = [[]]
  for x, y in ((2 ** p, m // (2 ** (p + 1)))
               for p in range(int(math.log(m, 2)))):
    k = min(y * 2 * k + 1, m - x)
    PAT_M.extend([m + 1] * (k + 3) for _ in range(x, 2 * x))
    _compute_pattern(w, w, k, m - x, x, 2 * x, PAT_M, PAT_M, True)
  return PAT_M

def _text_matching(t, w, n, m, k, PAT_M):
  TEXT_M = [[m + 1] * (k + 3) for _ in range(n - m + 1)]
  _compute_pattern(t, w, k, m, 0, n - m + 1, PAT_M, TEXT_M, False)
  return (i + 1 for i in range(n - m + 1) if TEXT_M[i][k + 1] == m + 1)

def landau_vishkin(t, w, n, m, k):
  def _pad_power_2(w, m):
    length = 2 ** math.ceil(math.log(m, 2))
    return w + '$' * (length - m), length
  if k > m:
    yield from range(1, n - m + 2)
  else:
    padded_word, padded_m = _pad_power_2(w, m)
    patterns = _pattern_matching(padded_word, k, padded_m)
    for i, pattern in enumerate(patterns):
      for j, v in enumerate(pattern):
        if v + i > m:
          patterns[i][j] = m + 1
    yield from _text_matching(t, w, n, m, k, patterns)

def bitap_shift_add(text: str, word: str, _n: int, m: int, k: int):
  # the alphabet we're working on
  A = set(text[1:])

  # number of bits required for each
  # position in the pattern
  B = math.ceil(math.log2(k+1)) + 1

  # bitmask of (m*B) ones for trimming
  # the state and overflow to length
  ones = (1 << (m*B)) - 1

  # the initial value for the state
  # as well as calculating the lookup
  initval = 0
  for _ in range(m):
    initval = (initval << B) | 1

  # overflow mask for clearing and
  # recording the overflow bits
  mask = 0
  for _ in range(m):
    mask = (mask << B) | (1 << (B-1))

  # lookup for each character
  # T[c] has 0 at i-th position iff word[i] == c
  # and 1 otherwise.
  # We ignore characters not in text
  # since we'll never look them up
  T = {c: initval for c in A}
  for (index, c) in enumerate(word[1:]):
    if c in A:
      T[c] = T[c] ^ (1 << (index*B))

  # the state (mismatches up to the i-th position)
  state = initval
  # overflow set, for recording
  # when the number of mismatches
  # exceeded `k` in the state
  overflow = mask

  for index, c in enumerate(text[1:], start = 1):
    # shift-add operation
    state = ((state << B) + T[c]) & ones

    # record overflow bits
    overflow = ((overflow << B) | (state & mask)) & ones

    # clear the overflow bits from state
    state &= ~mask

    # return a match when the number of mismatches
    # up to the m-the position (i.e. the whole pattern)
    # is at most than k (that is, state at m-th position
    # is less than k+1 and overflow isn't set)
    if (state | overflow) < ((k+1) << (m-1)*B):
      yield index-m+1

def _permutation_matching(t, w, n, m, k):
  Q, counter = collections.deque(), {}
  for c in w:
    if c not in counter:
      counter[c] = 1
    else:
      counter[c] += 1
  counter['#'] = 0
  Z = 0
  for j in range(1, n + 1):
    Q.append(t[j])
    counter[t[j]] -= 1
    if counter[t[j]] < 0:
      Z += 1
    # Pop from Q, until there are at most k mismatches
    while Z > k:
      x = Q.popleft()
      if counter[x] < 0:
        Z -= 1
      counter[x] += 1
    # Yield match and prepare Q for next iteration
    if len(Q) == m:
      yield j - m + 1
      x = Q.popleft()
      if counter[x] < 0:
        Z -= 1
      counter[x] += 1


def grossi_luccio_a3(t, w, n, m, k):
  A_w = set(w)
  t_sub = ''.join([c if c in A_w else '#' for c in t])
  for i in _permutation_matching(t_sub, w, n, m, k):
    if distance.hamming_distance('#' + t[i:i + m], w, m, m) <= k:
      yield i

# Returnes true iff H(P@T', P@T'[j:j+m]) <= k
# where P is the pattern
# T' is the text with characters not in P changed to `#`
# lcp is a longest common prefix structure for all suffixes in P@T'
def _mismatch(j, m, k, lcp):
  # Index in pattern
  w = 1
  # Index in text
  t = j
  # Mismatch counter
  c = 0
  # while index is still in pattern, and we don't have more than k mismatches
  # we get longest common prefix for P@T'[w:] and P@T'[t:]
  # if it extends pattern we have a match with c mistakes
  # else we get a mistake and search again after the found prefix
  while w <= m and c <= k:
    q = lcp.get(w, t)
    if w + q <= m:
      c += 1
    w = w + q + 1
    t = t + q + 1
  return c <= k


def _preorder_visit(ST, n, m, k, lcp, marked):
  result = []
  if ST.depth >= m > ST.parent.depth:
    leaves = ST.get_all_leaves(lambda x: x)
    if leaves[0].index in marked and _mismatch(
        m + n + 1 - leaves[0].depth + 2, m, k, lcp):
      return [n - l.depth + 2 for l in leaves if l.depth != n + m + 2]
  for child in ST.children.values():
    result += _preorder_visit(child, n, m, k, lcp, marked)
  return result


class LcpLinear:

  def __init__(self, w, _n, _ST):
    self.word = w

  def get(self, i, j):
    return prefix.get_longest_common_prefix(self.word[i:], self.word[j:])


class LcpLca:

  def __init__(self, _w, _n, ST):
    self.lca = lca.LCA(ST)
    leaves = ST.get_all_leaves(lambda x: (x.depth, x.index))
    self.nodes = [None] * (len(leaves) + 1)
    for (depth, index) in leaves:
      self.nodes[len(leaves) - depth + 1] = index

  def get(self, i, j):
    return self.lca.query_depth(self.nodes[i], self.nodes[j])


def grossi_luccio_a4(t, w, n, m, k, lcp_class):
  A_w = set(w[1:])
  t_sub = ''.join([c if c in A_w else '#' for c in t[1:]])
  w_t = w + '@' + t_sub
  ST, _ = suffix_tree.mccreight(w_t, n + m + 1)
  pi_occurences = [m + i + 1 for i in _permutation_matching('#'+t_sub, w, n, m, k)]
  ST.set_depth()
  ST.set_index()
  marked = {
    i
    for i in ST.get_all_leaves(lambda x: x.index
                   if m + n + 1 - x.depth + 2 in pi_occurences
                   or x.depth == n + m + 2 else None)
    if i is not None
  }
  lcp = lcp_class(w_t, n, ST)
  result = _preorder_visit(ST, n, m, k, lcp, marked)
  yield from result
