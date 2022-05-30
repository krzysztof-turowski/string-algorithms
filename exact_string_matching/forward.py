from common import prefix

def brute_force(t, w, n, m):
  i = 1
  while i <= n - m + 1:
    j = 0
    while j < m and t[i + j] == w[j + 1]:
      j = j + 1
    if j == m:
      yield i
    i = i + 1

def morris_pratt(t, w, n, m):
  B = prefix.prefix_suffix(w, m)
  i, j = 1, 0
  while i <= n - m + 1:
    while j < m and t[i + j] == w[j + 1]:
      j = j + 1
    if j == m:
      yield i
    i, j = i + j - B[j], max(0, B[j])

def knuth_morris_pratt(t, w, n, m):
  sB = prefix.strong_prefix_suffix(w, m)
  i, j = 1, 0
  while i <= n - m + 1:
    while j < m and t[i + j] == w[j + 1]:
      j = j + 1
    if j == m:
      yield i
    i, j = i + j - sB[j], max(0, sB[j])

def crochemore(t, w, n, m):
  def next_maximal_suffix(w, n, i, j, k, p):
    while j + k <= n:
      if w[i + k] == w[j + k]:
        if k == p:
          j, k = j + p, 1
        else:
          k += 1
      elif w[i + k] > w[j + k]:
        j, k, p = j + k, 1, j + k - i
      else:
        i, j, k, p = j, i + 1, 1, 1
    return i, j, k, p

  t_pos, w_pos = 0, 1
  i, j, k, p = 0, 1, 1, 1
  while t_pos <= n - m:
    while w_pos <= m and t[t_pos + w_pos] == w[w_pos]:
      w_pos += 1

    if w_pos == m + 1:
      yield t_pos + 1

    if t_pos == n - m:
      return

    i, j, k, p = next_maximal_suffix(
      w[:w_pos] + t[t_pos + w_pos], w_pos, i, j, k, p)

    w_ew_prim = w[i + 1:w_pos] + t[t_pos + w_pos]
    if w_ew_prim[:p].endswith(w[1:i + 1]):
      t_pos, w_pos = t_pos + p, w_pos - p + 1
      if j - i > p:
        j = j - p
      else:
        i, j, k, p = 0, 1, 1, 1
    else:
      t_pos, w_pos = t_pos + max(i, min(w_pos - i, j)) + 1, 1
      i, j, k, p = 0, 1, 1, 1
