def prefix_suffix(w, m):
  '''Computes table of prefix-suffix lengths for a word w'''
  B, t = [-1] + [0] * m, -1
  for i in range(1, m + 1):
    # niezmiennik: t = B[i - 1]
    while t >= 0 and w[t + 1] != w[i]:
      t = B[t] # prefikso-sufiks to relacja przechodnia
    t = t + 1
    B[i] = t
  return B

def period(w, m):
  return prefix_suffix(w, m)[m]

def strong_prefix_suffix(w, m):
  '''Computes table of strong prefix-suffix lengths for a word w'''
  sB, t = [-1] + [0] * m, -1
  for i in range(1, m + 1):
    # niezmiennik: t = B[i - 1]
    while t >= 0 and w[t + 1] != w[i]:
      t = sB[t]
    t = t + 1
    if i == m or w[t + 1] != w[i + 1]:
      sB[i] = t
    else:
      sB[i] = sB[t] # silny prefikso-sufiks slabego prefikso-sufiksu jest silny
  return sB

def prefix_suffix_from_strong_prefix_suffix(sB):
  n = len(sB)
  B = [0] * n
  B[0], B[-1] = -1, sB[-1]
  for i in range(n - 2, 1, -1):
    B[i] = max(B[i + 1] - 1, sB[i])
  return B

def prefix_prefix_brute_force(w, m):
  PREF = [-1] * (m + 1)
  for i in range(2, m + 1):
    for j in range(m + 1 - i, -1, -1):
      if w[i:i+j] == w[1:1+j]:
        PREF[i] = j
        break
  PREF[1] = m
  return PREF

def prefix_prefix(w, m):
  def naive_scan(i, j):
    r = 0
    while i + r <= m and j + r <= m and w[i + r] == w[j + r]:
      r += 1
    return r
  PREF, s = [-1] * 2 + [0] * (m - 1), 1
  for i in range(2, m + 1):
    # niezmiennik: s takie, że PREF[s] > 0 i s + PREF[s] - 1 jest maksymalne
    k = i - s + 1
    s_max = s + PREF[s] - 1
    if s_max < i:
      PREF[i] = naive_scan(i, 1)
      if PREF[i] > 0:
        s = i
    elif PREF[k] + k - 1 < PREF[s]:
      PREF[i] = PREF[k]
    else:
      PREF[i] = (s_max - i + 1) + naive_scan(s_max + 1, s_max - i + 2)
      s = i
  PREF[1] = m
  return PREF
