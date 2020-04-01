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
