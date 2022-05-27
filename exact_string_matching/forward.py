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
          j = j + p
          k = 1
        else:
          k = k +1
      elif w[i + k] > w[j + k]:
        j = j + k
        k = 1
        p = j - i
      else:
        i = j
        j = i + 1
        k = 1
        p = 1
    return (i, j, k, p)
  text_pos, w_pos = 0, 1
  i, j, k, p = 0, 1, 1, 1
  while text_pos <= n - m:
    while w_pos <= m and t[text_pos + w_pos] == w[w_pos]:
      w_pos = w_pos + 1

    if w_pos == m + 1:
      yield text_pos + 1

    if text_pos == n - m:
      return

    i, j, k, p = next_maximal_suffix(
      w[:w_pos] + t[text_pos + w_pos], w_pos, i, j, k, p)
    u_factor = w[1:i + 1]
    w_ew_prim = w[i + 1:w_pos] + t[text_pos + w_pos]
    w_factor = w_ew_prim[:p]
    if w_factor.endswith(u_factor):
      text_pos = text_pos + p
      w_pos = w_pos - p + 1
      if j - i > p:
        j = j - p
      else:
        i = 0
        j = 1
        k = 1
        p = 1
    else:
      text_pos = text_pos + max(i, min(w_pos - i, j)) + 1
      w_pos = 1
      i = 0
      j = 1
      k = 1
      p = 1
