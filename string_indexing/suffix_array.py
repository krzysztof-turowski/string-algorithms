from common import trie
from string_indexing import suffix_tree

def naive(text, n):
  text += '$'
  return [i for _, i in sorted([(text[i:], i) for i in range(1, n + 2)])]

def suffix_array_from_suffix_tree(text, n):
  def traverse(v, depth):
    depth -= len(v.label)
    if len(v.children) == 0:
      return [depth]
    return [d for _, child in sorted(v.children.items()) for d in traverse(child, depth)]
  ST, _ = suffix_tree.mccreight(text, n)
  return traverse(ST, n + 2)

def contains(SA, text, word, _, m):
  text += '$'
  left, right, low = -1, len(SA), 0
  while left + 1 < right:
    low = (left + right) // 2
    if word[1:] <= text[SA[low]:]:
      right = low
    else:
      left = low
  left, right, high = -1, len(SA), 0
  while left + 1 < right:
    high = (left + right) // 2
    if word[1:] < text[SA[high]:SA[high] + m]:
      right = high
    else:
      left = high
  yield from [SA[i] for i in range(low, high)]
