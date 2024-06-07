
class _RankSearcher:
  def __init__(self, L, mapper_of_chars, n):
    
    self.sample_size = 8 # const for sampling
    self.L = L
    
    #prepare closest samplings
    current_sample = 0
    self.closest_sample = [0]
    for i in range(1, n+2):
      if abs(current_sample-i) > abs(current_sample + self.sample_size-i) and (i + self.sample_size < n):
        current_sample += self.sample_size
      self.closest_sample.append(current_sample)

    #Generate values for occ for given samples O(|A|*n)
    self.occ_in_sample_for_char = { self.L[i]: [0] for i in range(1, n+2)}
    for c in mapper_of_chars:
      current_value = 0
      next_sample = self.sample_size
      for i in range(1, n+2):
        if L[i] == c:
          current_value += 1
        if i == next_sample:
          self.occ_in_sample_for_char[c].append(current_value)
          next_sample = next_sample + self.sample_size

  def prefix_rank(self, c, i):
    if self.closest_sample[i] < i:
      to_add = sum(1 for c_prim in self.L[self.closest_sample[i] + 1:i + 1] if c_prim == c)
    else:
      to_add = sum(-1 for c_prim in self.L[i + 1:self.closest_sample[i] + 1] if c_prim == c)
    return self.occ_in_sample_for_char[c][self.closest_sample[i] // self.sample_size] + to_add


class _FMIndex:
  def __init__ (self, SA, BWT, text, n, rank_searcher = None):
    self.L = BWT
    self.F = '#$' + ''.join(text[SA[i]] for i in range(1, n + 1))
    self.n = n
    self.SA = SA

    #prepare char mapping for F
    self.mapper_of_chars = { self.F[2] : 0}
    self.beginnings = [2]
    last = self.F[2]
    for i in range(3, n+2):
      if self.F[i] != last:
        last = self.F[i]
        self.beginnings.append(i)
        self.mapper_of_chars[last] = len(self.beginnings) - 1

    self.len_of_alphabet = len(self.mapper_of_chars)
    self.rank_searcher = _RankSearcher(self.L, self.mapper_of_chars, n) if rank_searcher is None else rank_searcher

def from_suffix_array_and_bwt(SA, BWT, text, n, rank_searcher = None):
  return _FMIndex(SA, BWT, text, n, rank_searcher)

# O(|p|)
def count(fm, p, size):
  (low, high) = _get_range_of_occurrences(fm, p, size)
  return max(high - low + 1, 0) if low > -1 else 0

# O(|p| + k) where k is the number or occurances of p in text
def contains(fm, p, l):
  (low, high) = _get_range_of_occurrences(fm, p, l)
  yield from sorted([fm.SA[i-1] for i in range(low, high + 1) if low > -1])

def _get_range_of_occurrences(fm, p, size):
  if size > fm.n or size == 0:
    return (-1, -1)

  if p[-1] not in fm.mapper_of_chars:
    return (-1, -1)

  map_idx = fm.mapper_of_chars[p[-1]]
  l = fm.beginnings[map_idx]
  r = fm.n + 1
  if map_idx != fm.len_of_alphabet - 1:
    r = fm.beginnings[map_idx + 1] - 1

  for i in range(size-1, 0, -1):
    if p[i] not in fm.mapper_of_chars:
      return (-1, -1)
    occurrences_before = fm.rank_searcher.prefix_rank(p[i], l - 1)
    occurrences_after = fm.rank_searcher.prefix_rank(p[i], r)
    if occurrences_before == occurrences_after:
      return (-1, -1)
    map_idx = fm.mapper_of_chars[p[i]]
    l = fm.beginnings[map_idx] + occurrences_before
    r = fm.beginnings[map_idx] + occurrences_after - 1
    if r < l:
      return (-1, -1)
  return (l, r)
