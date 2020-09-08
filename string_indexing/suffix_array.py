import collections
import enum
import itertools

PREFIX_TYPE = enum.IntEnum('PrefixType', 'LARGE SMALL', start = 0)
BUCKET_DIR = enum.IntEnum('BucketDir', {'FORWARD': 1, 'BACKWARD': -1})

def get_reverse(S):
  out = [0] * len(S)
  for i, v in enumerate(S):
    out[v - 1] = i + 1
  return out

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
  return get_reverse(R)

def skew(text, n):
  '''Computes suffix array using Kärkkäinen-Sanders algorithm'''
  def _convert(data):
    # zamiana tablicy liczb na string UTF-32 w tym samym porzadku znakow
    return '#' + ''.join(chr(ord('0') + v) for v in data)
  def _compare(i, j):
    if i % 3 == 1:
      return (text[i], S.get(i + 1, 0)) >= (text[j], S.get(j + 1, 0))
    return (text[i:i + 2], S.get(i + 2, 0)) >= (text[j:j + 2], S.get(j + 2, 0))

  if n <= 4:
    return naive(text, n)
  text += '$'
  P12 = list(range(1, n + 2, 3)) + list(range(2, n + 2, 3))
  triples = _rank([text[i:i + 3] for i in P12])
  recursion = skew(_convert(triples), (2 * n + 1) // 3 + 1)[1:]
  L12 = [P12[v - 1] for v in recursion]

  mapping = {v: i + 1 for i, v in enumerate(L12)}
  S = {v: mapping[v] for v in P12}

  P0 = [i for i in range(1, n + 2) if i % 3 == 0]
  tuples = [(text[i], S.get(i + 1, 0)) for i in P0]
  L0 = [P0[i - 1] for i in get_reverse(_rank(tuples))]
  return _merge(L12, L0, compare = _compare)

def _ternary_sort(I, begin, end, V, get_key_for_index):
  def get_pivot_first():
    return get_key_for_index(I[begin])

  if begin == end - 1:
    V[I[begin] - 1], I[begin] = begin, -1
  if end - begin < 2:
    return

  pivot, first_equal, last_equal = get_pivot_first(), begin, begin + 1
  for i in range(begin + 1, end):
    key = get_key_for_index(I[i])
    if key < pivot:
      I[first_equal], I[i] = I[i], I[first_equal]
      I[i], I[last_equal] = I[last_equal], I[i]
      first_equal, last_equal = first_equal + 1, last_equal + 1
    elif key == pivot:
      I[last_equal], I[i] = I[i], I[last_equal]
      last_equal += 1
  _ternary_sort(I, begin, first_equal, V, get_key_for_index)
  if last_equal - first_equal == 1:
    V[I[first_equal] - 1], I[first_equal] = first_equal, -1
  else:
    for i in range(first_equal, last_equal):
      V[I[i] - 1] = last_equal - 1
  _ternary_sort(I, last_equal, end, V, get_key_for_index)

def larsson_sadakane(text, n):
  text += '$'
  I = sorted(list(range(1, n + 2)), key = lambda index: text[index])

  V = [0] * (n + 1)
  current_index, current_symbol = n, text[I[n]]
  for i, v in enumerate(reversed(I)):
    if current_symbol != text[v]:
      current_index, current_symbol = n - i, text[v]
    V[v - 1] = current_index

  current_length, current_symbol = 0, '$'
  for i, current_suffix in enumerate(I):
    if current_symbol != text[current_suffix]:
      if current_length == 1:
        I[i - 1] = -1
      current_length, current_symbol = 0, text[current_suffix]
    current_length += 1

  k = 1
  while k <= n and I[0] != -(n + 1):
    i = 0
    while i <= n:
      if I[i] < 0:
        next_i = i - I[i]
        while next_i <= n and I[next_i] < 0:
          I[i], next_i = I[i] + I[next_i], next_i - I[next_i]
      else:
        next_i = V[I[i] - 1] + 1
        _ternary_sort(I, i, V[I[i] - 1] + 1, V, lambda index: V[index + k - 1])
      i = next_i
    k *= 2
  for i in range(n + 1):
    I[V[i]] = i + 1
  return I

class _SLText:
  def __init__(self, text):
    self.text = text
    self._get_ls_types()
    self.lms_positions = [
        i for i in range(2, len(self.types)) if self.is_lms(i)]

  def is_lms(self, i):
    return (i > 1 and (self.types[i - 1], self.types[i]) ==
            (PREFIX_TYPE.LARGE, PREFIX_TYPE.SMALL))

  def _get_ls_types(self):
    self.types = [PREFIX_TYPE.SMALL] * len(self.text)
    for i in range(len(self.text) - 2, 0, -1):
      if self.text[i] == self.text[i + 1]:
        self.types[i] = self.types[i + 1]
      elif self.text[i] >= self.text[i + 1]:
        self.types[i] = PREFIX_TYPE.LARGE

  def is_lms_equal(self, a, b):
    if a != b:
      for t, _ in enumerate(self.text):
        if (self.text[a + t] != self.text[b + t]
            or self.types[a + t] != self.types[b + t]):
          return False
        if t > 0 and (self.is_lms(a + t) or self.is_lms(b + t)):
          return True
    return True

def _induced_sort(sltext, initial):
  class _Buckets:
    def __init__(self, text, direction):
      self.target = [-1] * len(text)
      self._get_bucket_sizes(text)
      self.recompute(direction)

    def _get_bucket_sizes(self, text):
      self.sizes = [0] * (max(text) + 1)
      for c in text[1:]:
        self.sizes[c] += 1

    def recompute(self, direction):
      self.direction = direction
      heads = ([1] + self.sizes[:-1] if self.direction is BUCKET_DIR.FORWARD
               else self.sizes)
      self.heads = list(itertools.accumulate(heads))

    def set_and_advance(self, bucket, value):
      self.target[self.heads[bucket]] = value
      self.heads[bucket] += self.direction.value

  buckets = _Buckets(sltext.text, BUCKET_DIR.BACKWARD)
  for i in initial:
    buckets.set_and_advance(sltext.text[i], i)
  buckets.recompute(BUCKET_DIR.FORWARD)
  for i in range(1, len(sltext.text)):
    j = buckets.target[i] - 1
    if j > 0 and sltext.types[j] == PREFIX_TYPE.LARGE:
      buckets.set_and_advance(sltext.text[j], j)
  buckets.recompute(BUCKET_DIR.BACKWARD)
  for i in range(len(sltext.text) - 1, 0, -1):
    j = buckets.target[i] - 1
    if j > 0 and sltext.types[j] == PREFIX_TYPE.SMALL:
      buckets.set_and_advance(sltext.text[j], j)
  return buckets.target

def _rename_lms_substrings(sltext, suf):
  names, index, previous = [-1] * len(sltext.text), 0, suf[1]
  for i in suf[1:]:
    if sltext.is_lms(i):
      if not sltext.is_lms_equal(previous, i):
        index += 1
      names[i], previous = index, i
  return names

def _sa_distinct(text):
  result = [-1] * len(text)
  for i, c in enumerate(text[1:]):
    result[c + 1] = i + 1
  return result

def _induced_sorting(text, n):
  if n == 1:
    return [-1, 1]

  sltext = _SLText(text)
  suffixes = _induced_sort(sltext, initial = sltext.lms_positions)
  lms_names = _rename_lms_substrings(sltext, suffixes)
  reduced_text = [-1] + [lms_names[i] for i in sltext.lms_positions]
  reduced_array = (_induced_sorting(reduced_text, len(reduced_text) - 1)
                   if max(reduced_text) < len(reduced_text) - 2
                   else _sa_distinct(reduced_text))
  ordered_lms = [sltext.lms_positions[i - 1] for i in reduced_array[1:]]
  return _induced_sort(sltext, initial = ordered_lms[::-1])

def induced_sorting(text, n):
  '''Computes suffix array using Nong-Zhang-Chan algorithm'''
  return _induced_sorting([-1] + _rank(text[1:]) + [0], n + 1)[1:]

def _sort_category(s, SL, category):
  suffixes_by_distances, category_substring = _prepare_substring_lists(
      _bucket_array(s), SL, category)

  for i in range(1, len(suffixes_by_distances)):
    groups = suffixes_by_distances[i].sorted_groups()
    for g in groups if category == PREFIX_TYPE.SMALL else reversed(groups):
      to_split = collections.defaultdict(list)
      for j in suffixes_by_distances[i].index[g[0]:g[1]+1]:
        group_id = category_substring.group_id[
            category_substring.reversed_index[j - i]]
        to_split[group_id].append(j - i)

      for group_id in to_split:
        vals = to_split[group_id]
        if category == PREFIX_TYPE.SMALL:
          category_substring.split_group_before(vals)
        elif category == PREFIX_TYPE.LARGE:
          category_substring.split_group_after(vals)
        category_substring.reverse_group(
            category_substring.group_id[
                category_substring.reversed_index[vals[0]]])

  category_substring.refresh_group_ids()
  rec_s, m = [-1], { -1 : -1 }
  for i in range(1, len(s)):
    if SL[i] == category:
      m[len(m)] = i
      rec_s.append(
          category_substring.group_id[category_substring.reversed_index[i]])
  return [m[i] for i in _small_large(rec_s, len(rec_s) - 1)]

def _move_to_group_end(vals, condition, A, groups, front):
  for v in (v for v in vals if condition(v)):
    index = A.reversed_index[v]
    group_id = A.group_id[index]
    g = groups[group_id]
    if front:
      A.swap(index, g[0])
      groups[group_id] = (g[0] + 1, g[1])
    else:
      A.swap(index, g[1])
      groups[group_id] = (g[0], g[1] - 1)

def _prepare_substring_lists(A, SL, category):
  category_distance = _get_category_distance(SL, category)
  suffixes_by_distances = [
      GroupedArray() for _ in range(max(category_distance) + 1)]
  category_substrings = GroupedArray()

  for g in A.sorted_groups():
    category_substrings.append_group(
        [A.index[i] for i in range(g[0], g[1] + 1)
         if SL[A.index[i]] == category])
  for g in A.sorted_groups():
    to_add = collections.defaultdict(list)
    for x in (A.index[i] for i in range(g[0], g[1] + 1)):
      to_add[category_distance[x]].append(x)
    for d in to_add:
      suffixes_by_distances[d].append_group(to_add[d])
  return (suffixes_by_distances, category_substrings)

def _bucket_array(s):
  buckets, A = [[] for _ in range (len(s))], GroupedArray()
  for i, e in enumerate(s[1:], start = 1):
    buckets[e].append(i)
  for b in (b for b in buckets if len(b) > 0):
    A.append_group(b)
  return A

def _categorize_sl(s, n):
  SL, i = [None], 1
  while i < len(s) - 1:
    j = next(j for j in range(i + 1, len(s)) if s[i] != s[j])
    SL.extend(
        [PREFIX_TYPE.LARGE if s[i] > s[j] else PREFIX_TYPE.SMALL] * (j - i))
    i = j
  SL.append(PREFIX_TYPE.SMALL if SL.count(PREFIX_TYPE.SMALL) <= n // 2
            else PREFIX_TYPE.LARGE)
  return SL

def _get_category_distance(SL, category):
  i = next(i for i, x in enumerate(SL[1:], 1) if x == category)
  category_distance, dist_from_last = [-1] + [0] * i, 0
  while i < len(SL) - 1:
    if SL[i] == category:
      dist_from_last = 0
    dist_from_last, i = dist_from_last + 1, i + 1
    category_distance.append(dist_from_last)
  return category_distance

class GroupedArray:
  def __init__(self):
    self.index, self.group_id, self.next_free_id = [-1], [-1], 0
    self.reversed_index, self.groups = {}, {}

  def sorted_groups(self):
    g, i = [], 1
    while i < len(self.index):
      group_id = self.group_id[i]
      g.append(self.groups[group_id])
      i = self.groups[group_id][1] + 1
    return g

  def refresh_group_ids(self):
    groups = {}
    for g in self.sorted_groups():
      group_id = len(groups)
      groups[group_id] = g
      for i in range(g[0], g[1] + 1):
        self.group_id[i] = group_id
    self.next_free_id, self.groups = len(groups), groups

  def swap(self, i, j):
    index, reversed_index = self.index, self.reversed_index
    reversed_index[index[i]], reversed_index[index[j]] = \
        reversed_index[index[j]], reversed_index[index[i]]
    index[i], index[j] = index[j], index[i]

  def swap_by_value(self, a, b):
    self.swap(self.reversed_index[a], self.reversed_index[b])

  def append_group(self, vals):
    group_id, self.next_free_id = self.next_free_id, self.next_free_id + 1
    g = (len(self.index), len(self.index) + len(vals) - 1)
    self.groups[group_id] = g
    self.group_id.extend([group_id] * len(vals))
    self.index.extend(vals)
    for i in range(g[0], g[1] + 1):
      self.reversed_index[self.index[i]] = i

  def split_group_after(self, vals):
    new_id = self.next_free_id
    old_id = self.group_id[self.reversed_index[vals[0]]]
    old = self.groups[old_id]
    self.next_free_id += 1
    s = old[1] - len(vals) + 1
    for r, v in zip(range(old[1], s - 1, -1), reversed(vals)):
      self.swap_by_value(self.index[r], v)
      self.group_id[r] = new_id
    self.groups[new_id], self.groups[old_id] = (s, old[1]), (old[0], s - 1)

  def split_group_before(self, vals):
    new_id = self.next_free_id
    old_id = self.group_id[self.reversed_index[vals[0]]]
    old = self.groups[old_id]
    self.next_free_id += 1
    s = old[0] + len(vals)
    for l, v in zip(range(old[0], s), vals):
      self.swap_by_value(self.index[l], v)
      self.group_id[l] = new_id
    self.groups[new_id], self.groups[old_id] = (old[0], s - 1), (s, old[1])

  def reverse_group(self, group_id):
    l, r = self.groups[group_id]
    while l < r:
      self.swap(l, r)
      l, r = l + 1, r - 1

def _small_large(text_int, n):
  A, SL = _bucket_array(text_int), _categorize_sl(text_int, n)
  if n == 2:
    return [2, 1]
  if SL.count(PREFIX_TYPE.LARGE) == 1:
    return [n] + list(range(1, n))
  if SL.count(PREFIX_TYPE.SMALL) == 1:
    return list(reversed(range(1, n + 1)))

  if SL[-1] == PREFIX_TYPE.SMALL:
    sortedS = _sort_category(text_int, SL, PREFIX_TYPE.SMALL)
    groups = A.groups.copy()
    _move_to_group_end(
        reversed(sortedS[1:]), lambda x: True, A, groups, front = False)
    _move_to_group_end(
        (A.index[i] - 1 for i in range(1, len(A.index))),
        lambda x: SL[x] == PREFIX_TYPE.LARGE, A, groups, front = True)
  else:
    sortedL = _sort_category(text_int, SL, PREFIX_TYPE.LARGE)
    groups = A.groups.copy()
    _move_to_group_end(sortedL[1:], lambda x: True, A, groups, front = True)
    _move_to_group_end(
        (A.index[i] - 1 for i in reversed(range(1, len(A.index)))),
        lambda x: SL[x] == PREFIX_TYPE.SMALL, A, groups, front = False)
  return A.index[1:]

def small_large(text, n):
  '''Computes suffix array using Ko-Aluru algorithm'''
  return _small_large([-1] + _rank(text[1:]) + [0], n + 1)

def from_suffix_tree(ST, n):
  ST.set_depth()
  return ST.get_all_leaves(lambda x: n + 2 - x.depth)

def contains(SA, text, word, n, m):
  def _binary_search(f):
    left, right = -1, n + 1
    while left + 1 < right:
      mid = (left + right) // 2
      if f(mid):
        right = mid
      else:
        left = mid
    return right
  # Najmniejszy sufiksu nie większy niż szukane słowo
  low = _binary_search(lambda x: word[1:] <= text[SA[x]:])
  # Najmniejszy sufiks większego niż m-literowy prefiks szukanego słowa
  high = _binary_search(lambda x: word[1:] < text[SA[x]:SA[x] + m])
  yield from sorted([SA[i] for i in range(low, high)])
