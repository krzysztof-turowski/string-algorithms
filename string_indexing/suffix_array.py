def _reverse(S):
  reverse = [0] * len(S)
  for i, _ in enumerate(S):
    reverse[S[i] - 1] = i + 1
  return reverse

def _rank(S):
  mapping = {v: i + 1 for i, v in enumerate(sorted(set(S)))}
  return [mapping[v] for v in S]

def _merge(A, B, compare):
  out, a, b = [0] * (len(A) + len(B)), 0, 0
  for i, _ in enumerate(out):
    if b >= len(B):
      out[i], a = A[a], a + 1
    elif a >= len(A) or compare(A[a], B[b]):
      out[i], b = B[b], b + 1
    else:
      out[i], a = A[a], a + 1
  return out

def naive(text, n):
  text += '$'
  return [i for _, i in sorted([(text[i:], i) for i in range(1, n + 2)])]

def prefix_doubling(text, n):
  '''Computes suffix array using Karp-Miller-Rosenberg algorithm'''
  text += '$'
  R, k = _rank(text[1:]), 1
  while k < 2 * n:
    pairs = [(R[i], R[i + k] if i + k < len(R) else 0) for i in range(len(R))]
    R, k = _rank(pairs), 2 * k
  return _reverse(R)

def skew(text, n):
  '''Computes suffix array using Kärkkäinen-Sanders algorithm'''
  def convert(data):
    # zamiana tablicy liczb na string UTF-32 w tym samym porzadku znakow
    return '#' + ''.join(chr(ord('0') + v) for v in data)
  def compare(i, j):
    if i % 3 == 1:
      return (text[i], S.get(i + 1, 0)) >= (text[j], S.get(j + 1, 0))
    return (text[i:i + 2], S.get(i + 2, 0)) >= (text[j:j + 2], S.get(j + 2, 0))

  if n <= 4:
    return naive(text, n)
  text += '$'
  P12 = [i for i in range(1, n + 2) if i % 3 == 1] \
      + [i for i in range(1, n + 2) if i % 3 == 2]
  triples = _rank([text[i:i + 3] for i in P12])
  recursion = skew(convert(triples), (2 * n + 1) // 3 + 1)[1:]
  L12 = [P12[v - 1] for v in recursion]

  mapping = {v: i + 1 for i, v in enumerate(L12)}
  S = {v: mapping[v] for v in P12}

  P0 = [i for i in range(1, n + 2) if i % 3 == 0]
  tuples = [(text[i], S.get(i + 1, 0)) for i in P0]
  L0 = [P0[i - 1] for i in _reverse(_rank(tuples))]
  return _merge(L12, L0, compare = compare)

def induced_sorting(text, n):
  '''Computes suffix array using Nong-Zhang-Chan algorithm'''
  raise NotImplementedError

def from_suffix_tree(ST, n):
  ST.set_depth()
  return ST.get_all_leaves(lambda x: n + 2 - x.depth)

def contains(SA, text, word, n, m):
  def binary_search(f):
    left, right = -1, n + 1
    while left + 1 < right:
      mid = (left + right) // 2
      if f(mid):
        right = mid
      else:
        left = mid
    return right
  # Najmniejszy sufiksu nie większy niż szukane słowo
  low = binary_search(lambda x: word[1:] <= text[SA[x]:])
  # Najmniejszy sufiks większego niż m-literowy prefiks szukanego słowa
  high = binary_search(lambda x: word[1:] < text[SA[x]:SA[x] + m])
  yield from sorted([SA[i] for i in range(low, high)])

def lcp_from_suffix_array(SA, text, n):
  text += '$'
  return [-1] + [
      next(i for i, x, y in zip(range(n), text[i:], text[j:]) if x != y)
      for i, j in zip(SA, SA[1:])]

def lcp_from_suffix_tree(ST):
  def _get_lcp(v):
    if len(v.children) == 0:
      return []
    L = [lcp for _, child in sorted(v.children.items())
         for lcp in _get_lcp(child) + [v.depth]]
    return L[:-1]
  ST.set_depth()
  return [-1] + _get_lcp(ST)

def lcp_kasai(SA, text, n):
  text += '$'
  L = [-1] * (n + 1)
  R, k = _reverse(SA), 0
  for i in range(1, n + 2):
    if k > 0:
      k -= 1
    if R[i - 1] == n + 1:
      k = 0
    else:
      j = SA[R[i - 1]]
      while i + k <= n and j + k <= n and text[i + k] == text[j + k]:
        k += 1
      L[R[i - 1]] = k;
  return L
