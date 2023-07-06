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
  maximum_suffix = [max(i, 0) for i in suffix.maximum_suffixes(w[:-1], m - 1)]
  def check_ends(i, k):
    return maximum_suffix[i - 1] >= min(k, i) - 1
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

def boyer_moore_apostolico_giancarlo_bad_shift(t, w, n, m):
  maximum_suffix = [max(i, 0) for i in suffix.maximum_suffixes(w[:-1], m - 1)]
  def check_ends(i, k):
    return maximum_suffix[i - 1] >= min(k, i) - 1
  BM = suffix.boyer_moore_shift(w, m)
  LAST = suffix.last_occurrence(w[:-1])
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
    bad_character = LAST.get(t[i + j - 1], 0)
    i = i + max(BM[j], j - bad_character)

def bitap_shift_add(text: str, word: str, _n: int, m: int):
  A = set(text[1:]) | set(word[1:])

  ones = (1 << m) - 1

  T = {c: ones for c in A}
  for index, c in enumerate(word[1:]):
    T[c] = T[c] ^ (1<<index)

  state = ones

  for index, c in enumerate(text[1:], start = 1):
    state = ((state << 1) | T[c]) & ones
    if state & (1<<(m-1)) == 0:
      yield index-m+1
