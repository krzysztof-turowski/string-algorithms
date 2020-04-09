from common import trie
from generator import rand
from string_indexing import suffix_tree

SUFFIX_TREE_ALGORITHMS = [
    suffix_tree.weiner,
    suffix_tree.mccreight,
    suffix_tree.ukkonen,
]

def random_suffix_tree_test(n, A):
  t = rand.random_word(n, A)
  reference_result = suffix_tree.naive(t, n)
  for algorithm in SUFFIX_TREE_ALGORITHMS:
    result, _ = algorithm(t, n)
    assert trie.TrieNode.compare(reference_result, result)

def random_suffix_links_test(n, A):
  t = rand.random_word(n, A)
  mccreight = suffix_tree.mccreight(t, n)
  mccreight[0].set_index()
  mccreight_result = sorted([(u.index, v.index) for u, v in mccreight[1].items()])
  ukkonen = suffix_tree.ukkonen(t, n)
  ukkonen[0].set_index()
  ukkonen_result = sorted([(u.index, v.index) for u, v in ukkonen[1].items()])
  assert trie.TrieNode.compare(mccreight[0], ukkonen[0])
  assert mccreight_result == ukkonen_result

for _ in range(200):
  random_suffix_tree_test(1000, ['a', 'b'])
for _ in range(200):
  random_suffix_links_test(1000, ['a', 'b'])
