from common import prefix

def weak_boyer_moore_shift_brute_force(w, m):
  B = prefix.prefix_suffix(w, m)
  wBM = [m] * m + [B[m]]
  for i in range(1, m + 1):
    for s in range(1, m + 1):
      start = max(i, s) + 1
      if w[start - s:-s] == w[start:]:
        wBM[i] = s
        break
  wBM[0] = wBM[1]
  return wBM

def weak_boyer_moore_shift(w, m):
  # TODO: implement O(m) algorithm
  return weak_boyer_moore_shift_brute_force(w, m)

def boyer_moore_shift_brute_force(w, m):
  B = prefix.prefix_suffix(w, m)
  BM = [m] * m + [B[m]]
  for i in range(m):
    for s in range(1, m):
      start = max(i, s) + 1
      if w[start - s:-s] == w[start:] and (s >= i or w[i - s] != w[i]):
        BM[i] = s
        break
  return BM

def maximum_suffixes(w, m):
  w_rev = w[0] + w[-1:0:-1]
  PREF = prefix.prefix_prefix(w_rev, m)
  S = [PREF[0]] + PREF[-1:0:-1]
  return S

def boyer_moore_shift(w, m):
  B = prefix.prefix_suffix(w, m)
  BM = [m] * m + [B[m]]
  S, j = maximum_suffixes(w, m), 0
  for k in range(m - 1, -1, -1):
    if k == S[k]:
      while j < m - k:
        BM[j] = m - k
        j += 1
  for k in range(1, m):
    BM[m - S[k]] = m - k
  return BM

def last_occurrence(w, m):
  LAST = {}
  for i, v in enumerate(w[1:]):
    LAST[v] = i + 1
  return LAST
