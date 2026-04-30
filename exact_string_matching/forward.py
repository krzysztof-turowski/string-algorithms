from dataclasses import dataclass
from typing import List, Tuple
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

@dataclass
class _Hrp:
  period: int
  scope: Tuple[int, int]

def galil_seifaras(t, w, n, m, k = 4):
  def get_hrp(w, m, k):
    '''Yields k-Highly-Repeating-Prefixes (k-HRP),
    i.e. basic periods with at least k periods.'''
    period, j = 1, 0
    hrps: List[_Hrp] = []
    while period + j < m:
      while period + j < m and w[j + 1] == w[period + j + 1]:
        j += 1
      if period * (k - 1) <= j:
        hrps.append(_Hrp(period = period, scope = (2 * period, period + j)))
        yield hrps[-1]
      hrp = next((h for h in hrps if 2 * h.scope[0] <= j <= h.scope[1]), None)
      if hrp is not None:
        period, j = period + hrp.period, j - hrp.period
      else:
        period, j = period + (j // k) + 1, 0

  def perfect_decomposition(w, m, k):
    '''Returns strings u, v and k-HRP of v,
    such that w = u*v and v has only one k-HRP'''
    hrp_generator = get_hrp(w, m, k)
    j, hrp1, hrp2 = 0, next(hrp_generator, None), next(hrp_generator, None)
    while hrp1 is not None and hrp2 is not None:
      j += hrp1.period
      hrp_generator = get_hrp(w[j:], m - j, k)
      hrp1 = next(hrp_generator, None)
      if hrp1 and hrp1.period >= hrp2.period:
        hrp2 = next(hrp_generator, None)
    return w[:j + 1], '#' + w[j + 1:], j, m - j, hrp1

  def simple_text_search(t, w, n, m, hrp1: _Hrp, k):
    '''Iterates over every occurrence of pattern w in text t.
    Assumes w has only one k-HRP hrp1.'''
    i, j = 0, 0
    while i + m <= n:
      while j < m and w[j + 1] == t[i + j + 1]:
        j += 1
      if j == m:
        yield i + 1
      if hrp1 and 2 * hrp1.scope[0] <= j <= hrp1.scope[1]:
        i, j = i + hrp1.period, j - hrp1.period
      else:
        i, j = i + (j // k) + 1, 0

  u, v, u_size, v_size, hrp1 = perfect_decomposition(w, m, k)
  for i in simple_text_search(t, v, n, v_size, hrp1, k):
    if i > u_size and u[1:] == t[i - u_size:i]:
      yield i - u_size

def crochemore(t, w, n, m):
  def next_maximal_suffix(w, m, i, j, k, p):
    while j + k <= m:
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

  x, y = 0, 1
  i, j, k, p = 0, 1, 1, 1
  while x <= n - m:
    while y <= m and t[x + y] == w[y]:
      y += 1
    if y == m + 1:
      yield x + 1
    if x == n - m:
      return
    i, j, k, p = next_maximal_suffix(w[:y] + t[x + y], y, i, j, k, p)
    w_prim = w[i + 1:y] + t[x + y]
    if w_prim[:p].endswith(w[1:i + 1]):
      x, y = x + p, y - p + 1
      if j - i > p:
        j = j - p
      else:
        i, j, k, p = 0, 1, 1, 1
    else:
      x, y = x + max(i, min(y - i, j)) + 1, 1
      i, j, k, p = 0, 1, 1, 1
