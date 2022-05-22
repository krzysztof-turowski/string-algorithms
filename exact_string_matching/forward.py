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

def _preprocess_first_two_hrps(w, m, k):
  '''Compute first two  k-Highly-Repeating-Prefix (k-HRP).

  A prefix is k-HRP if it is basic period with at least k periods.
  '''
  period, j = 1, 0
  hrp1 = None
  while period + j < m:
    while period + j < m and w[j + 1] == w[period + j + 1]:
      j += 1
    prefix_len = period + j

    if period * k <= prefix_len:
      next_hrp = (period, prefix_len)
      if hrp1 is not None:
        return hrp1, next_hrp
      hrp1 = next_hrp

    if hrp1 is not None and hrp1[0] * 2 <= j <= hrp1[1]:
      period += hrp1[0]
      j -= hrp1[0]
    else:
      period += (j // k) + 1
      j = 0

  return hrp1, None


def _perfect_factorization(w, m, k):
  '''Returns strings u, v and k-HRP of v,
  such that w = u*v and v has only one k-HRP
  '''
  j = 0
  hrp1, hrp2 = _preprocess_first_two_hrps(w, m, k)

  while hrp1 is not None and hrp2 is not None:
    j += hrp1[0]
    hrp1, next_hrp2 = _preprocess_first_two_hrps(w[j:], m - j, k)
    if hrp1 is not None and hrp1[0] >= hrp2[0]:
      hrp2 = next_hrp2

  return w[:j+1], w[j:], j, m - j, hrp1


def _simple_text_search(t, v, n, m, hrp1, k):
  '''Iterates over every occurrence of pattern v in text t.

  Assumes v has only one k-HRP hrp1.
  '''
  pos, j = 0, 0
  while pos + m <= n:
    while j < m and v[j+1] == t[pos + j + 1]:
      j += 1

    if j == m:
      yield pos + 1

    if hrp1 is not None and 2 * hrp1[0] <= j <= hrp1[1]:
      pos = pos + hrp1[0]
      j = j - hrp1[0]
    else:
      pos += (j // k) + 1
      j = 0

def galil_seifaras(t, w, n, m):
  k = 4
  u, v, uLen, vLen, hrp1 = _perfect_factorization(w, m, k)
  for i in _simple_text_search(t, v, n, vLen, hrp1, k):
    if i > uLen and u[1:] == t[i - uLen :i]:
      yield i - uLen
