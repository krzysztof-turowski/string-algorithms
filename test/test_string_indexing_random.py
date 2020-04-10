from common import trie
from generator import rand
from string_indexing import suffix_tree, suffix_array

SUFFIX_TREE_ALGORITHMS = [
    suffix_tree.weiner,
    suffix_tree.mccreight,
    suffix_tree.ukkonen,
]

SUFFIX_ARRAY_ALGORITHMS = [
    suffix_array.prefix_doubling,
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
  mccreight_result = sorted(
      [(u.index, v.index) for u, v in mccreight[1].items()])
  ukkonen = suffix_tree.ukkonen(t, n)
  ukkonen[0].set_index()
  ukkonen_result = sorted([(u.index, v.index) for u, v in ukkonen[1].items()])
  assert trie.TrieNode.compare(mccreight[0], ukkonen[0])
  assert mccreight_result == ukkonen_result

def random_backward_suffix_links_test(n, A):
  t = rand.random_word(n, A)
  mccreight = suffix_tree.mccreight(t, n)
  mccreight[0].set_index()
  mccreight_result = sorted(
      [(u.index, v.index) for u, v in mccreight[1].items()])
  weiner = suffix_tree.weiner(t, n)
  weiner[0].set_index()
  weiner_result = sorted(
      [(v.index, u.index) for (u, _), v in weiner[1].items()])
  assert trie.TrieNode.compare(mccreight[0], weiner[0])
  assert mccreight_result == weiner_result

def random_suffix_array_test(n, A):
  t = rand.random_word(n, A)
  reference_result = suffix_array.naive(t, n)
  for algorithm in SUFFIX_ARRAY_ALGORITHMS:
    result = algorithm(t, n)
    assert result == reference_result
  assert suffix_array.suffix_array_from_suffix_tree(
      suffix_tree.mccreight(t, n)[0], n) == reference_result

for _ in range(200):
  random_suffix_tree_test(1000, ['a', 'b'])
for _ in range(200):
  random_suffix_links_test(1000, ['a', 'b'])
for _ in range(200):
  random_backward_suffix_links_test(1000, ['a', 'b'])
for _ in range(200):
  random_suffix_array_test(1000, ['a', 'b'])
