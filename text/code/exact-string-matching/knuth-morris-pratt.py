def knuth_morris_pratt_string_matching(t, w, m, n):
  sB = strong_prefix_suffix(w)
  i = 0
  while i <= n - m + 1:
    j = 0
    while j < m and t[i + j + 1] == w[j + 1]:
      j = j + 1
    if j == m:
      return True
    i, j = i + j - sB[j], max(0, sB[j])
  return False