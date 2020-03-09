from common import prefix

def brute_force(t, w, n, m):
  for i in range(n - m + 1):
    j = 0
    while j < m and t[i + j + 1] == w[j + 1]:
      j = j + 1
    if j == m:
      return True
  return False

def morris_pratt(t, w, n, m):
  B = prefix.prefix_suffix(w, m)
  i = 0
  while i <= n - m + 1:
    j = 0
    while j < m and t[i + j + 1] == w[j + 1]:
      j = j + 1
    if j == m:
      return True
    i, j = i + j - B[j], max(0, B[j])
  return False

def knuth_morris_pratt(t, w, n, m):
  sB = prefix.strong_prefix_suffix(w, m)
  i = 0
  while i <= n - m + 1:
    j = 0
    while j < m and t[i + j + 1] == w[j + 1]:
      j = j + 1
    if j == m:
      return True
    i, j = i + j - sB[j], max(0, sB[j])
  return False
