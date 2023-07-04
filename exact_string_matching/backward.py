from common import suffix

def brute_force(t, w, n, m):
  i = 1
  while i <= n - m + 1:
    j = m
    while j > 0 and t[i + j - 1] == w[j]:
      j = j - 1
    if j == 0:
      yield i
    i = i + 1

def weak_boyer_moore(t, w, n, m):
  wBM = suffix.weak_boyer_moore_shift(w, m)
  i = 1
  while i <= n - m + 1:
    j = m
    while j > 0 and t[i + j - 1] == w[j]:
      j = j - 1
    if j == 0:
      yield i
    i = i + wBM[j]

def boyer_moore(t, w, n, m):
  BM = suffix.boyer_moore_shift(w, m)
  i = 1
  while i <= n - m + 1:
    j = m
    while j > 0 and t[i + j - 1] == w[j]:
      j = j - 1
    if j == 0:
      yield i
    i = i + BM[j]

def boyer_moore_galil(t, w, n, m):
  BM = suffix.boyer_moore_shift(w, m)
  i, memory = 1, 0
  while i <= n - m + 1:
    j = m
    while j > memory and t[i + j - 1] == w[j]:
      j = j - 1
    if j == memory:
      yield i
      i, memory = i + BM[0], m - BM[0]
    else:
      i, memory = i + BM[j], 0

def boyer_moore_bad_shift(t, w, n, m):
  BM, LAST = suffix.boyer_moore_shift(w, m), suffix.last_occurrence(w[:-1])
  i = 1
  while i <= n - m + 1:
    j = m
    while j > 0 and t[i + j - 1] == w[j]:
      j = j - 1
    if j == 0:
      yield i
    bad_character = LAST.get(t[i + j - 1], 0)
    i = i + max(BM[j], j - bad_character)

def bad_shift_heuristic(t, w, n, m):
  LAST = suffix.last_occurrence(w)
  i = 1
  while i <= n - m + 1:
    j = m
    while j > 0 and t[i + j - 1] == w[j]:
      j = j - 1
    if j == 0:
      yield i
    bad_character = LAST.get(t[i + j - 1], 0)
    i = i + max(1, j - bad_character)

def quick_search(t, w, n, m):
  LAST = suffix.last_occurrence(w)
  i = 1
  while i <= n - m + 1:
    j = 1
    while j <= m and t[i + j - 1] == w[j]:
      j = j + 1
    if j == m + 1:
      yield i
    bad_character = LAST.get(t[i + m], 0) if i + m <= n else 0
    i = i + (m + 1 - bad_character)

def horspool(t, w, n, m):
  LAST = suffix.last_occurrence(w[:-1])
  i = 1
  while i <= n - m + 1:
    c = t[i + m - 1]
    if w[m] == c:
      j = 1
      while j < m and t[i + j - 1] == w[j]:
        j = j + 1
      if j == m:
        yield i
    bad_character = LAST.get(c, 0)
    i = i + (m - bad_character)

def turbo_boyer_moore(t, w, n, m):
  BM = suffix.boyer_moore_shift(w, m)
  i, memory, shift = 1, 0, 0
  while i <= n - m + 1:
    j = m
    while j > 0 and t[i + j - 1] == w[j]:
      if memory != 0 and j == m - shift:
        j = j - memory
      else:
        j = j - 1
    if j == 0:
      yield i
    match = m - j
    turbo_shift = memory - match
    shift = max(BM[j], turbo_shift)
    if shift > BM[j]:
      i = i + max(shift, match + 1)
      memory = 0
    else:
      i = i + shift
      memory = min(m - shift, match)


def boyer_moore_apostolico_giancarlo(t, w, n, m):
  def check_ends(i, k):
    return w[max(0, i - k) + 1:i] == w[m - min(k, i) + 1:m]
  BM = suffix.boyer_moore_shift(w, m)
  skip = [0] * (n + 1)
  i = 1
  while i <= n - m + 1:
    j = m
    while j > 0:
      if check_ends(j, skip[i + j - 1]) and t[i + j - 1] == w[j]:
        j = j - max(1, skip[i + j - 1])
      else:
        break
    if j <= 0:
      yield i
      j = 1
    skip[i + m - 1] = m - j
    i = i + BM[j]

def bitap_shift_add(t, w, n, m):
  A = set(t[1:]) | set(w[1:])
  ones = (1 << m) - 1
  T = {c: ones for c in A}
  for i, c in enumerate(w[1:]):
    T[c] ^= (1 << i)
  state = ones
  for i, c in enumerate(t[1:], start = 1):
    state = ((state << 1) | T[c]) & ones
    if state & (1 << (m - 1)) == 0:
      yield i - m + 1
