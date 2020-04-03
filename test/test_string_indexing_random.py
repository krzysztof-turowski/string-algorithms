from common import trie
from generator import rand
from string_indexing import suffix_tree

def random_suffix_tree_test(T, A):
  t = rand.random_word(T, A)
  reference_result = suffix_tree.naive(t, len(t) - 1)
  for algorithm in [suffix_tree.mccreight, suffix_tree.ukkonen]:
    result, _ = algorithm(t, len(t) - 1)
    assert trie.TrieNode.compare(reference_result, result)

def random_suffix_links_test(T, A):
  t = rand.random_word(T, A)
  mccreight = suffix_tree.mccreight(t, len(t) - 1)
  mccreight[0].set_index()
  mccreight_result = sorted([(u.index, v.index) for u, v in mccreight[1].items()])
  ukkonen = suffix_tree.ukkonen(t, len(t) - 1)
  ukkonen[0].set_index()
  ukkonen_result = sorted([(u.index, v.index) for u, v in ukkonen[1].items()])
  assert trie.TrieNode.compare(mccreight[0], ukkonen[0])
  assert mccreight_result == ukkonen_result

for i in range(200):
  random_suffix_tree_test(1000, ['a', 'b'])
for i in range(200):
  random_suffix_links_test(1000, ['a', 'b'])
