def prefix_prefix(w, m):
  def naive_scan(i, j):
    r = 0
    while i + r <= m and j + r <= m and w[i + r] == w[j + r]:
      r += 1
    return r
  PREF, s = [-1] * 2 + [0] * (m - 1), 1
  for i in range(2, m + 1):
    # niezmiennik: s jest takie, ze s + PREF[s] - 1 jest maksymalne i PREF[s] > 0
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