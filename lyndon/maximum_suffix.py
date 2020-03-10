def maximum_suffix(w, m):
  B, out = [-1] + [0] * m, 1
  for i in range(1, m + 1):
    # niezmiennik: B[j] = prefix_suffix(maximum_suffix(w[1..j])) dla j < i
    t = B[i - 1]
    while t >= 0 and w[out + t] < w[i]:
      out, t = i - t, B[t]
    while t >= 0 and w[out + t] != w[i]:
      t = B[t]
    B[i] = t + 1
  return out
