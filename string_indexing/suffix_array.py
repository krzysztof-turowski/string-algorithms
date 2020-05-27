import collections
import enum

def _reverse(S):
  reverse = [0] * len(S)
  for i, _ in enumerate(S):
    reverse[S[i] - 1] = i + 1
  return reverse

def _rank(S):
  mapping = {v: i + 1 for i, v in enumerate(sorted(set(S)))}
  return [mapping[v] for v in S]

def _merge(A, B, compare):
  out, a, b = [0] * (len(A) + len(B)), 0, 0
  for i, _ in enumerate(out):
    if b >= len(B):
      out[i], a = A[a], a + 1
    elif a >= len(A) or compare(A[a], B[b]):
      out[i], b = B[b], b + 1
    else:
      out[i], a = A[a], a + 1
  return out

def naive(text, n):
  text += '$'
  return [i for _, i in sorted([(text[i:], i) for i in range(1, n + 2)])]

def prefix_doubling(text, n):
  '''Computes suffix array using Karp-Miller-Rosenberg algorithm'''
  text += '$'
  R, k = _rank(text[1:]), 1
  while k < 2 * n:
    pairs = [(R[i], R[i + k] if i + k < len(R) else 0) for i in range(len(R))]
    R, k = _rank(pairs), 2 * k
  return _reverse(R)

def skew(text, n):
  '''Computes suffix array using Kärkkäinen-Sanders algorithm'''
  def convert(data):
    # zamiana tablicy liczb na string UTF-32 w tym samym porzadku znakow
    return '#' + ''.join(chr(ord('0') + v) for v in data)
  def compare(i, j):
    if i % 3 == 1:
      return (text[i], S.get(i + 1, 0)) >= (text[j], S.get(j + 1, 0))
    return (text[i:i + 2], S.get(i + 2, 0)) >= (text[j:j + 2], S.get(j + 2, 0))

  if n <= 4:
    return naive(text, n)
  text += '$'
  P12 = [i for i in range(1, n + 2) if i % 3 == 1] \
      + [i for i in range(1, n + 2) if i % 3 == 2]
  triples = _rank([text[i:i + 3] for i in P12])
  recursion = skew(convert(triples), (2 * n + 1) // 3 + 1)[1:]
  L12 = [P12[v - 1] for v in recursion]

  mapping = {v: i + 1 for i, v in enumerate(L12)}
  S = {v: mapping[v] for v in P12}

  P0 = [i for i in range(1, n + 2) if i % 3 == 0]
  tuples = [(text[i], S.get(i + 1, 0)) for i in P0]
  L0 = [P0[i - 1] for i in _reverse(_rank(tuples))]
  return _merge(L12, L0, compare = compare)

def induced_sorting(text, n):
  '''Computes suffix array using Nong-Zhang-Chan algorithm'''
  raise NotImplementedError

def _map_string(s):
  sorted_char_set = sorted(set( c for c in s[1:] ))
  char_to_ord = { c : i for i, c in enumerate(sorted_char_set, 1) }
  return [0] + [ char_to_ord[c] for c in s[1:] ] + [0]

def small_large(text, n):
  Category = enum.Enum("Category", "L S")

  def _small_large(s):
    A, SL, N = _bucket_array(s), _categorize_sl(s), len(s)-1
    if N == 2:
      return [2, 1]
    if SL.count(Category.L) == 1:
      return [N] + list(range(1, N))
    if SL.count(Category.S) == 1:
      return list(reversed(range(1, N + 1)))

    if SL[-1] == Category.S:
      sortedS = _sort_category(s, SL, Category.S)
      groups = A.groups.copy()
      _move_to_group_end(
          reversed(sortedS[1:]),
          lambda x: True, False, A, groups)
      _move_to_group_end(
          map(lambda i : A.tab[i] - 1, range(1, len(A.tab))),
          lambda x: SL[x] == Category.L, True, A, groups)
    elif SL[-1] == Category.L:
      sortedL = _sort_category(s, SL, Category.L)
      groups = A.groups.copy()
      _move_to_group_end(sortedL[1:], lambda x: True, True, A, groups)
      _move_to_group_end(
          map(lambda i : A.tab[i] - 1, reversed(range(1, len(A.tab)))),
          lambda x: SL[x] == Category.S, False, A, groups)
    else:
      raise Exception("fail")

    return A.tab[1:]

  def _sort_category(s, SL, category):
    suff_by_dist, categ_substr = _prepare_substr_lists(
        _bucket_array(s), SL, category)

    # sort categ_substr
    for i in range(1, len(suff_by_dist)):
      groups = suff_by_dist[i].sorted_groups()
      for g in groups if category == Category.S else reversed(groups):
        to_split = collections.defaultdict(list)
        for j in suff_by_dist[i].tab[g[0]:g[1]+1]:
          x = j-i
          g_id = categ_substr.group_id[categ_substr.rev[x]]
          to_split[g_id].append(x)

        for g_id in to_split:
          vals = to_split[g_id]
          if category == Category.S:
            categ_substr.split_group_before(vals)
            categ_substr.reverse_group(
                categ_substr.group_id[categ_substr.rev[vals[0]]])
          elif category == Category.L:
            categ_substr.split_group_after(vals)
            categ_substr.reverse_group(
                categ_substr.group_id[categ_substr.rev[vals[0]]])

    # map Ssubstr to ints
    categ_substr.refresh_group_ids()
    rec_s, m = [-1], { -1 : -1 }
    for i in range(1, len(s)):
      if SL[i] == category:
        m[len(m)] = i
        rec_s.append(categ_substr.group_id[categ_substr.rev[i]])

    # recursive call and undo mapping
    return [ m[i] for i in _small_large(rec_s) ]

  def _move_to_group_end(vals, condition, front, A, groups):
    for v in vals:
      if not condition(v):
        continue
      idx = A.rev[v]
      g_id = A.group_id[idx]
      g = groups[g_id]

      if front:
        A.swap(idx, g[0])
        groups[g_id] = (g[0]+1, g[1])
      else:
        A.swap(idx, g[1])
        groups[g_id] = (g[0], g[1]-1)

  def _prepare_substr_lists(A, SL, category):
    categDist = _calc_category_dist(SL, category)
    suff_by_dist = [ GroupedArray() for _ in range (max(categDist)+1) ]
    category_substr = GroupedArray()

    for g in A.sorted_groups():
      to_add = []
      for i in range(g[0], g[1]+1):
        x = A.tab[i]
        if SL[x] == category:
          to_add.append(x)
      category_substr.append_group(to_add)

    for g in A.sorted_groups():
      to_add = collections.defaultdict(list)
      for i in range(g[0], g[1]+1):
        x = A.tab[i]
        d = categDist[x]
        to_add[d].append(x)
      for d in to_add:
        suff_by_dist[d].append_group(to_add[d])

    return (suff_by_dist, category_substr)

  def _bucket_array(s):
    buckets, A = [ [] for _ in range (len(s)) ], GroupedArray()
    for i in range(1, len(s)):
      buckets[s[i]].append(i)
    for b in filter(lambda b: len(b) > 0, buckets):
      A.append_group(b)
    return A

  def _categorize_sl(s):
    SL, i = [ "." ], 1
    while i < len(s)-1:
      j = i+1
      while s[i] == s[j]:
        j += 1
      l = j-i
      SL.extend([Category.L if s[i] > s[j] else Category.S] * l)
      i = j
    N = len(s)-1
    SL.append(Category.S if SL.count(Category.S) <= N/2 else Category.L)
    return SL


  def _calc_category_dist(SL, category):
    i = next(i for i, x in enumerate(SL[1:], 1) if x == category)
    categDist, dist_from_last = [-1] + [0] * i, 0
    while i < len(SL)-1:
      if SL[i] == category:
        dist_from_last = 0
      dist_from_last += 1
      i += 1
      categDist.append(dist_from_last)
    return categDist

  class GroupedArray:
    def __init__(self):
      self.tab, self.group_id = [-1], [-1]
      self.rev, self.groups = {}, {}
      self.next_free_id = 0

    def sorted_groups(self):
      g, i = [], 1
      while i < len(self.tab):
        g_id = self.group_id[i]
        g.append(self.groups[g_id])
        i = self.groups[g_id][1] + 1
      return g

    def refresh_group_ids(self):
      groups = {}
      for g in self.sorted_groups():
        g_id = len(groups)
        groups[g_id] = g
        for i in range(g[0], g[1]+1):
          self.group_id[i] = g_id
      self.next_free_id, self.groups = len(groups), groups

    def swap(self, i, j):
      tab, rev = self.tab, self.rev
      rev[tab[i]], rev[tab[j]] = rev[tab[j]], rev[tab[i]]
      tab[i], tab[j] = tab[j], tab[i]

    def swap_by_val(self, a, b):
      self.swap(self.rev[a], self.rev[b])

    def append_group(self, vals):
      g_id = self.next_free_id
      self.next_free_id += 1
      g = (len(self.tab), len(self.tab) + len(vals) -1)
      self.groups[g_id] = g
      self.group_id.extend([g_id] * len(vals))
      self.tab.extend(vals)
      for i in range(g[0], g[1]+1):
        self.rev[self.tab[i]] = i


    def split_group_after(self, vals):
      new_g_id, old_g_id = self.next_free_id, self.group_id[self.rev[vals[0]]]
      old_g = self.groups[old_g_id]
      self.next_free_id += 1
      s = old_g[1] - len(vals) +1
      for r, v in zip(range(old_g[1], s-1, -1), reversed(vals)):
        self.swap_by_val(self.tab[r], v)
        self.group_id[r] = new_g_id
      self.groups[new_g_id], self.groups[old_g_id] =(s,old_g[1]),(old_g[0],s-1)

    def split_group_before(self, vals):
      new_g_id, old_g_id = self.next_free_id, self.group_id[self.rev[vals[0]]]
      old_g = self.groups[old_g_id]
      self.next_free_id += 1
      s = old_g[0] + len(vals)
      for l, v in zip(range(old_g[0], s), vals):
        self.swap_by_val(self.tab[l], v)
        self.group_id[l] = new_g_id
      self.groups[new_g_id], self.groups[old_g_id] =(old_g[0],s-1),(s,old_g[1])

    def reverse_group(self, g_id):
      l, r = self.groups[g_id]
      while l < r:
        self.swap(l, r)
        l += 1
        r -= 1

  return _small_large(_map_string(text))

def from_suffix_tree(ST, n):
  ST.set_depth()
  return ST.get_all_leaves(lambda x: n + 2 - x.depth)

def contains(SA, text, word, n, m):
  def binary_search(f):
    left, right = -1, n + 1
    while left + 1 < right:
      mid = (left + right) // 2
      if f(mid):
        right = mid
      else:
        left = mid
    return right
  # Najmniejszy sufiksu nie większy niż szukane słowo
  low = binary_search(lambda x: word[1:] <= text[SA[x]:])
  # Najmniejszy sufiks większego niż m-literowy prefiks szukanego słowa
  high = binary_search(lambda x: word[1:] < text[SA[x]:SA[x] + m])
  yield from sorted([SA[i] for i in range(low, high)])

def lcp_from_suffix_array(SA, text, n):
  text += '$'
  return [-1] + [
      next(i for i, x, y in zip(range(n), text[i:], text[j:]) if x != y)
      for i, j in zip(SA, SA[1:])]

def lcp_from_suffix_tree(ST):
  def _get_lcp(v):
    if len(v.children) == 0:
      return []
    L = [lcp for _, child in sorted(v.children.items())
         for lcp in _get_lcp(child) + [v.depth]]
    return L[:-1]
  ST.set_depth()
  return [-1] + _get_lcp(ST)

def lcp_kasai(SA, text, n):
  text += '$'
  L = [-1] * (n + 1)
  R, k = _reverse(SA), 0
  for i in range(1, n + 2):
    if R[i - 1] != n + 1:
      j = SA[R[i - 1]]
      while i + k <= n and j + k <= n and text[i + k] == text[j + k]:
        k += 1
      L[R[i - 1]] = k
      k = max(k - 1, 0)
    else:
      k = 0
  return L
