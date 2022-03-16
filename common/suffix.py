from common import prefix

def weak_boyer_moore_shift_brute_force(w, m):
  wBM = [m] * (m + 1)
  for i in range(1, m + 1):
    for s in range(1, m + 1):
      start = max(i, s) + 1
      if w[start - s:-s] == w[start:]:
        wBM[i] = s
        break
  wBM[0] = wBM[1]
  return wBM

def weak_boyer_moore_shift(w, m):
  S, j = maximum_suffixes(w, m), 0
  l_prim = [0] * (m + 1)
  for k in range(m - 1, -1, -1):
    if k == S[k]:
      while j < m - k:
        l_prim[j] = k
        j += 1
  L = [0] * (m + 1)
  for k in range(1, m):
    L[m - S[k]] = k
  for k in range(2, m + 1):
    L[k] = max(L[k - 1], L[k])
  wBM = [m - (L[k] if L[k] > 0 else l_prim[k]) for k in range(m + 1)]
  return wBM

def boyer_moore_shift_brute_force(w, m):
  BM = [m] * (m + 1)
  for i in range(m + 1):
    for s in range(1, m + 1):
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
  S, j = maximum_suffixes(w, m), 0
  l_prim = [0] * (m + 1)
  for k in range(m - 1, -1, -1):
    if k == S[k]:
      while j < m - k:
        l_prim[j] = k
        j += 1
  L_prim = [0] * (m + 1)
  for k in range(1, m):
    L_prim[m - S[k]] = k
  BM = [m - (L_prim[k] if L_prim[k] > 0 else l_prim[k]) for k in range(m + 1)]
  return BM

def last_occurrence(w):
  LAST = {}
  for i, v in enumerate(w[1:], start = 1):
    LAST[v] = i
  return LAST
