import collections

def reverse(SA):
  reverse = [0] * len(SA)
  for i in range(len(SA)):
    reverse[SA[i] - 1] = i + 1
  return reverse

def naive(text, n):
  text += '$'
  return [i for _, i in sorted([(text[i:], i) for i in range(1, n + 2)])]

def prefix_doubling(text, n):
  '''Computes suffix array using Karp-Miller-Rosenberg algorithm'''
  text += '$'
  mapping = {v: i + 1 for i, v in enumerate(sorted(set(text[1:])))}
  R, k = [mapping[v] for v in text[1:]], 1
  while k < 2 * n:
    pairs = [(R[i], R[i + k] if i + k < len(R) else 0) for i in range(len(R))]
    mapping = {v: i + 1 for i, v in enumerate(sorted(set(pairs)))}
    R, k = [mapping[pair] for pair in pairs], 2 * k
  return reverse(R)

def skew(text, n):
  '''Computes suffix array using Kärkkäinen-Sanders algorithm'''
  pass

def induced_sorting(text, n):
  '''Computes suffix array using Nong-Zhang-Chan algorithm'''
  pass

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
