import collections

def naive(text, n):
  text += '$'
  return [i for _, i in sorted([(text[i:], i) for i in range(1, n + 2)])]

def prefix_doubling(text, n):
  '''Computes suffix array using Manber-Myers algorithm'''
  text += '$'
  def sort_suffixes(indices, order):
    d = collections.defaultdict(list)
    for i in indices:
      key = text[i + order // 2:i + order]
      d[key].append(i)
    result = []
    for _, v in sorted(d.items()):
      if len(v) > 1:
        result += sort_suffixes(v, 2 * order)
      else:
        result.append(v[0])
    return result
  return sort_suffixes(range(1, n + 2), 1)

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
