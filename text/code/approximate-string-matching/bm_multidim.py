def boyer_moore_multi_dim_shift(A, p, m, k):
  ready = {a: m + 1 for a in A}
  BM_k = {(i, a): m for a in A for i in range(m, m - k - 1, -1)}
  for i in range(m - 1, 0, -1):
    for j in range(ready[p[i]] - 1, max(i, m - k) - 1, -1):
      BM_k[(j, p[i])] = j - i
    ready[p[i]] = max(i, m - k)
  return BM_k