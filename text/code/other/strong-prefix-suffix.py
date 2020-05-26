def strong_prefix_suffix(w, m):
  sB, t = [-1] + [0] * m, -1
  for i in range(1, m + 1): # niezmiennik: t = B[i - 1]
    while t >= 0 and w[t + 1] != w[i]:
      t = sB[t]
    t = t + 1
    if i == m or w[t + 1] != w[i + 1]:
      sB[i] = t
    else:
      sB[i] = sB[t]
  return sB