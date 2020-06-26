  j = m
  while j <= n + k:
    r, i, = k, m
    bad = 0         # counts bad indexes
    d = m           # initial value of shift
    while i > k >= bad:
      if i >= m - k:
        d = min(d, BM_k[(i, t[r])])
      if BAD[(i, t[r])]:
        bad = bad + 1
      i, r = i - 1, r - 1

    if bad <= k:
      mark D(0,j-m-k),...,D(0,j-m+k)
    j = j + max(k + 1, d)