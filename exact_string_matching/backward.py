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

def boyer_moore_bad_shift(t, w, n, m):
  BM, LAST = suffix.boyer_moore_shift(w, m), suffix.last_occurrence(w)
  i = 1
  while i <= n - m + 1:
    j = m
    while j > 0 and t[i + j - 1] == w[j]:
      j = j - 1
    if j == 0:
      yield i
    bad_character = LAST.get(t[i + j - 1], 0) if i + j <= n else 0
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
    bad_character = LAST.get(t[i + j - 1], 0) if i + j <= n else 0
    i = i + max(1, j - bad_character)
