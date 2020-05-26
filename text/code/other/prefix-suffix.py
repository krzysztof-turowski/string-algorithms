def prefix_suffix(w, m):
  B, t = [-1] + [0] * m, -1
  for i in range(1, m + 1):
    while t >= 0 and w[t + 1] != w[i]:
      t = B[t] # prefikso-sufiks to relacja przechodnia
    t = t + 1
    B[i] = t
  return B