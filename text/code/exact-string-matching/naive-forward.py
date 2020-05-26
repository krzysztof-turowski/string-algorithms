def naive_string_matching(t, w, n, m):
  for i in range(n - m + 1):
    j = 0
    while j < m and t[i + j + 1] == w[j + 1]:
      j = j + 1
    if j == m:
      return True
  return False