import collections
import enum

Category = enum.Enum("Category", "L S")

def small_large(text, text_len):
  return _small_large(_map_string(text), text_len+1)

def _map_string(s):
  sorted_char_set = sorted(set( c for c in s[1:] ))
  char_to_ord = { c : i for i, c in enumerate(sorted_char_set, 1) }
  return [0] + [ char_to_ord[c] for c in s[1:] ] + [0]

def _small_large(s, n):
  A, SL = _bucket_array(s), _categorize_sl(s, n)
  if n == 2:
    return [2, 1]
  if SL.count(Category.L) == 1:
    return [n] + list(range(1, n))
  if SL.count(Category.S) == 1:
    return list(reversed(range(1, n+1)))

  if SL[-1] == Category.S:
    sortedS = _sort_category(s, SL, Category.S)
    groups = A.groups.copy()
    _move_to_group_end(
        reversed(sortedS[1:]), lambda x: True, A, groups, front=False)
    _move_to_group_end(
        (A.tab[i]-1 for i in range(1, len(A.tab))),
        lambda x: SL[x] == Category.L, A, groups, front=True)
  elif SL[-1] == Category.L:
    sortedL = _sort_category(s, SL, Category.L)
    groups = A.groups.copy()
    _move_to_group_end(sortedL[1:], lambda x: True, A, groups, front=True)
    _move_to_group_end(
        (A.tab[i]-1 for i in reversed(range(1, len(A.tab)))),
        lambda x: SL[x] == Category.S, A, groups, front=False)
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
  return [ m[i] for i in _small_large(rec_s, len(rec_s)-1) ]

def _move_to_group_end(vals, condition, A, groups, front):
  for v in (v for v in vals if condition(v)):
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
    category_substr.append_group(
        [ A.tab[i] for i in range(g[0], g[1]+1) if SL[A.tab[i]] == category ])

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
  for i, e in enumerate(s[1:], start=1):
    buckets[e].append(i)
  for b in (b for b in buckets if len(b) > 0):
    A.append_group(b)
  return A

def _categorize_sl(s, n):
  SL, i = [ "." ], 1
  while i < len(s)-1:
    j = next(j for j in range(i + 1, len(s)) if s[i] != s[j])
    l = j-i
    SL.extend([Category.L if s[i] > s[j] else Category.S] * l)
    i = j
  SL.append(Category.S if SL.count(Category.S) <= n/2 else Category.L)
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
