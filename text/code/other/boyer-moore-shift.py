def boyer_moore_shift(w, m):
  B = prefix.prefix_suffix(w, m)
  BM = [m - B[m]] + [m] * m
  S, j = maximum_suffixes(w, m), 0
  for k in range(m - 1, -1, -1):
    if k == S[k]:
      while j < m - k:
        BM[j] = m - k
        j += 1
  for k in range(1, m):
    BM[m - S[k]] = m - k
  return BM