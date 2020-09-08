import math

from approximate_string_matching import distance

def naive_edit_distance(t, w, n, m, k):
  D = distance.distance_row(
      w, t, m, n, distance.EDIT_DISTANCE, distance.FirstRow.ZEROS)
  for i, v in enumerate(D[1:]):
    if v <= k:
      yield i + 1

def _next_possible_occurence(t, n, m, k, BM_k, BAD, j):
  while j <= n + k:
    r, i, bad, d = j, m, 0, m
    while i > k >= bad:
      if i >= m - k and r <= n:
        d = min(d, BM_k[(i, t[r])])
      if r <= n and BAD[(i, t[r])]:
        bad += 1
      i, r = i - 1, r - 1
    if bad <= k and j <= n + k:
      npo = j - m - k
      j += max(k + 1, d)
      return npo, j
    j += max(k + 1, d)
  return n + 1, j

def _boyer_moore_bad_environment(p, m, k, A):
  bad_table = {(i, a): True for i in range(1, m + 1) for a in A}
  for i in range(1, m + 1):
    for j in range(max(0, i - k), min(i + k, m) + 1):
      bad_table[(j, p[i])] = False
  return bad_table

def _boyer_moore_shift(p, m, k, A):
  ready = {a: m + 1 for a in A}
  BM_k = {(i, a): m for a in A for i in range(m, m - k - 1, -1)}
  for i in range(m - 1, 0, -1):
    for j in range(ready[p[i]] - 1, max(i, m - k) - 1, -1):
      BM_k[(j, p[i])] = j - i
    ready[p[i]] = max(i, m - k)
  return BM_k

def approximate_boyer_moore(t, p, n, m, k):
  A = set(list(t[1:] + p[1:]))
  BM_k = _boyer_moore_shift(p, m, k, A)
  BAD = _boyer_moore_bad_environment(p, m, k, A)

  j, top, D_0 = m, min(k + 1, m), list(range(m + 1))
  current, j = _next_possible_occurence(t, n, m, k, BM_k, BAD, j)
  current = max(current, 1)
  D, last = D_0[:], current + m + 2 * k

  while current <= n:
    for r in range(current, last + 1):
      c = 0
      for i in range(1, top + 1):
        d = (c if r <= n and p[i] == t[r] else min(D[i - 1], D[i], c) + 1)
        c, D[i] = D[i], d
      while D[top] > k:
        top -= 1
      if top == m:
        if r <= n:
          yield r
      else:
        top += 1
    next_possible, j = _next_possible_occurence(t, n, m, k, BM_k, BAD, j)
    if next_possible > last + 1:
      D, top, current = D_0[:], min(k + 1, m), next_possible
    else:
      current = last + 1
    last = next_possible + m + 2 * k

def naive_hamming(t, w, n, m, k):
  for i in range(1, n - m + 2):
    if distance.hamming_distance('#' + t[i:i + m], w, m, m) <= k:
      yield i

def _compute_pattern(
    t, w, k, length, b_frst_mm_p, last, PAT_M, TEXT_M, is_pattern):

  def _extend_pattern(cur_p, frst_p, found_mm):
    frst_p = max(frst_p, cur_p) + 1
    while(found_mm < k + 1 and (frst_p - cur_p <= length)
          and not (is_pattern and frst_p >= len(w))):
      if t[frst_p] != w[frst_p-cur_p]:
        found_mm += 1
        TEXT_M[cur_p][found_mm] = frst_p - cur_p
      frst_p += 1
    return frst_p - 1

  def _merge_pattern(cur_p, b_frst_mm_p, frst_p):
    t_it, p_it, no_mm = 0, 1, 0
    for x in range(1, k + 3):
      if b_frst_mm_p + TEXT_M[b_frst_mm_p][x] > cur_p :
        t_it = x
        break

    w_slide = cur_p - b_frst_mm_p
    while not(no_mm == k+1 or t_it == k+2 or
              (cur_p + PAT_M[w_slide][p_it]>frst_p
               and TEXT_M[b_frst_mm_p][t_it] == len(w))):
      if (cur_p + PAT_M[w_slide][p_it] >
          b_frst_mm_p + TEXT_M[b_frst_mm_p][t_it]):
        no_mm += 1
        TEXT_M[cur_p][no_mm] = TEXT_M[b_frst_mm_p][t_it] - w_slide
        t_it += 1
      elif (cur_p + PAT_M[w_slide][p_it] <
            b_frst_mm_p + TEXT_M[b_frst_mm_p][t_it]):
        no_mm += 1
        TEXT_M[cur_p][no_mm] = PAT_M[cur_p - b_frst_mm_p][p_it]
        p_it += 1
      else:
        if w[PAT_M[w_slide][p_it]] != t[cur_p+PAT_M[w_slide][p_it]]:
          no_mm +=1
          TEXT_M[cur_p][no_mm] = PAT_M[w_slide][p_it]
        p_it +=1
        t_it +=1
    return no_mm

  frst_p = b_frst_mm_p
  for cur_p in range(b_frst_mm_p, last):
    if is_pattern:
      frst_p = min(frst_p, len(w) - 1)
    found_mm = _merge_pattern(
        cur_p, b_frst_mm_p, frst_p) if cur_p < frst_p else 0
    if found_mm < k + 1:
      b_frst_mm_p = 1 if is_pattern else cur_p
      frst_p = _extend_pattern(cur_p, frst_p, found_mm)

def _pattern_matching(w: str, k: int, m: int):
  PAT_M = [[]]
  for x, y in ((2 ** p, m // (2 ** (p + 1)))
               for p in range(int(math.log(m, 2)))):
    k = min(y * 2 * k + 1, m - x)
    PAT_M.extend([m + 1] * (k + 3) for _ in range(x, 2 * x))
    _compute_pattern(w, w, k, m - x, x, 2 * x, PAT_M, PAT_M, True)
  return PAT_M

def _text_matching(t, w, n, m, k, PAT_M):
  TEXT_M = [[m + 1] * (k + 3) for _ in range(n - m + 1)]
  _compute_pattern(t, w, k, m, 0, n - m + 1, PAT_M, TEXT_M, False)
  return (i + 1 for i in range(n - m + 1) if TEXT_M[i][k + 1] == m + 1)

def landau_vishkin(t, w, n, m, k):
  def _pad_power_2(w, m):
    length = 2 ** math.ceil(math.log(m, 2))
    return w + '$' * (length - m), length
  if k > m:
    yield from range(1, n - m + 2)
  else:
    padded_word, padded_m = _pad_power_2(w, m)
    patterns = _pattern_matching(padded_word, k, padded_m)
    for i, pattern in enumerate(patterns):
      for j, v in enumerate(pattern):
        if v + i > m:
          patterns[i][j] = m + 1
    yield from _text_matching(t, w, n, m, k, patterns)
