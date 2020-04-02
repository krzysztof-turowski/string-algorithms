def naive(text, n):
  text += '$'
  return [i for _, i in sorted([(text[i:], i) for i in range(1, n + 2)])]

def suffix_array_from_suffix_tree(ST, n):
  def traverse(v, depth):
    depth -= len(v.label)
    if len(v.children) == 0:
      return [depth]
    return [d for _, child in sorted(v.children.items()) for d in traverse(child, depth)]
  return traverse(ST, n + 2)

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
  # Pozycja najmniejszego sufiksu nie większego niż szukane słowo
  low = binary_search(lambda x: word[1:] <= text[SA[x]:])
  # Pozycja najmniejszego sufiksu większego niż szukane słowo na pierwszych m literach
  high = binary_search(lambda x: word[1:] < text[SA[x]:SA[x] + m])
  yield from sorted([SA[i] for i in range(low, high)])
