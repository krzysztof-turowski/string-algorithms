def prefix_suffix(w, m):
  '''Computes table of prefix-suffix lengths for a word w'''
  B, t = [-1] + [0] * m, -1
  for i in range(1, m + 1):
    while t >= 0 and w[t + 1] != w[i]:
      t = B[t] # prefikso-sufiks to relacja przechodnia
    t = t + 1
    B[i] = t
  return B

def strong_prefix_suffix(w, m):
  '''Computes table of strong prefix-suffix lengths for a word w'''
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

def prefix_suffix_from_strong_prefix_suffix(sB):
  n = len(sB)
  B = [0] * n
  B[0], B[-1] = -1, sB[-1]
  for i in range(n - 2, 1, -1):
    B[i] = max(B[i + 1] - 1, sB[i])
  return B
