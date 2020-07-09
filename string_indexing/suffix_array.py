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
  def _convert(data):
    # zamiana tablicy liczb na string UTF-32 w tym samym porzadku znakow
    return '#' + ''.join(chr(ord('0') + v) for v in data)
  def _compare(i, j):
    if i % 3 == 1:
      return (text[i], S.get(i + 1, 0)) >= (text[j], S.get(j + 1, 0))
    return (text[i:i + 2], S.get(i + 2, 0)) >= (text[j:j + 2], S.get(j + 2, 0))

  if n <= 4:
    return naive(text, n)
  text += '$'
  P12 = list(range(1, n + 2, 3)) + list(range(2, n + 2, 3))
  triples = _rank([text[i:i + 3] for i in P12])
  recursion = skew(_convert(triples), (2 * n + 1) // 3 + 1)[1:]
  L12 = [P12[v - 1] for v in recursion]

  mapping = {v: i + 1 for i, v in enumerate(L12)}
  S = {v: mapping[v] for v in P12}

  P0 = [i for i in range(1, n + 2) if i % 3 == 0]
  tuples = [(text[i], S.get(i + 1, 0)) for i in P0]
  L0 = [P0[i - 1] for i in _reverse(_rank(tuples))]
  return _merge(L12, L0, compare = _compare)

def _ternary_sort(I, begin, end, V, get_key_for_index):
  def get_pivot_first():
    return get_key_for_index(I[begin])

  if begin == end - 1:
    V[I[begin] - 1], I[begin] = begin, -1
  if end - begin < 2:
    return

  pivot, first_equal, last_equal = get_pivot_first(), begin, begin + 1
  for i in range(begin + 1, end):
    key = get_key_for_index(I[i])
    if key < pivot:
      I[first_equal], I[i] = I[i], I[first_equal]
      I[i], I[last_equal] = I[last_equal], I[i]
      first_equal, last_equal = first_equal + 1, last_equal + 1
    elif key == pivot:
      I[last_equal], I[i] = I[i], I[last_equal]
      last_equal += 1
  _ternary_sort(I, begin, first_equal, V, get_key_for_index)
  if last_equal - first_equal == 1:
    V[I[first_equal] - 1], I[first_equal] = first_equal, -1
  else:
    for i in range(first_equal, last_equal):
      V[I[i] - 1] = last_equal - 1
  _ternary_sort(I, last_equal, end, V, get_key_for_index)

def larsson_sadakane(text, n):
  text += '$'
  I = sorted(list(range(1, n + 2)), key = lambda index: text[index])

  V = [0] * (n + 1)
  current_index, current_symbol = n, text[I[n]]
  for i, v in enumerate(reversed(I)):
    if current_symbol != text[v]:
      current_index, current_symbol = n - i, text[v]
    V[v - 1] = current_index

  current_length, current_symbol = 0, '$'
  for i, current_suffix in enumerate(I):
    if current_symbol != text[current_suffix]:
      if current_length == 1:
        I[i - 1] = -1
      current_length, current_symbol = 0, text[current_suffix]
    current_length += 1

  k = 1
  while k <= n and I[0] != -(n + 1):
    i = 0
    while i <= n:
      if I[i] < 0:
        next_i = i - I[i]
        while next_i <= n and I[next_i] < 0:
          I[i], next_i = I[i] + I[next_i], next_i - I[next_i]
      else:
        next_i = V[I[i] - 1] + 1
        _ternary_sort(I, i, V[I[i] - 1] + 1, V, lambda index: V[index + k - 1])
      i = next_i
    k *= 2
  for i in range(n + 1):
    I[V[i]] = i + 1
  return I

def induced_sorting(text, n):
  '''Computes suffix array using Nong-Zhang-Chan algorithm'''
  raise NotImplementedError

def from_suffix_tree(ST, n):
  ST.set_depth()
  return ST.get_all_leaves(lambda x: n + 2 - x.depth)

def contains(SA, text, word, n, m):
  def _binary_search(f):
    left, right = -1, n + 1
    while left + 1 < right:
      mid = (left + right) // 2
      if f(mid):
        right = mid
      else:
        left = mid
    return right
  # Najmniejszy sufiksu nie większy niż szukane słowo
  low = _binary_search(lambda x: word[1:] <= text[SA[x]:])
  # Najmniejszy sufiks większego niż m-literowy prefiks szukanego słowa
  high = _binary_search(lambda x: word[1:] < text[SA[x]:SA[x] + m])
  yield from sorted([SA[i] for i in range(low, high)])
