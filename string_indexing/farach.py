import enum
import math

from common import trie
from common.lca import LCA
from string_indexing import suffix_tree as sufftree

class _NodeType(enum.IntFlag):
  NONE = 0
  ODD = 1
  EVEN = 2
  BOTH = 3

class _TrieNodeWithType(trie.TrieNode):
  def __init__(self, label, node_type = _NodeType.NONE):
    self.node_type = node_type
    super().__init__(label)

def counting_sort(A, ind):
  n = max(max(*a) for a in A) + 1
  result, count = [0] * len(A), [0] * n
  for tp in A:
    count[tp[ind]] += 1
  for i in range(1, n):
    count[i] += count[i - 1]
  for tp in reversed(A):
    count[tp[ind]] -= 1
    result[count[tp[ind]]] = tp
  return result

def radix_sort(A, upper_index = 2):
  for i in reversed(range(upper_index)):
    A = counting_sort(A, i)
  return A

def _initialise_odd_even_pairs_recurse(node, n, odd_even_pairs):
  if not node.children:
    odd = node.index if node.node_type & _NodeType.ODD else None
    even = node.index if node.node_type & _NodeType.EVEN else None
    odd_even_pairs[node.index] = (odd, even)
    return

  for child in node.children.values():
    _initialise_odd_even_pairs_recurse(child, n, odd_even_pairs)
  odd = odd_second = even = even_second = odd_index = even_index = None
  for child in node.children.values():
    o, e = odd_even_pairs[child.index]
    if o and odd is None:
      odd, odd_index = o, child.index
    elif o and odd_second is None:
      odd_second = o
    if e and even is None:
      even, even_index = e, child.index
    elif e and even_second is None:
      even_second = e
  if odd_index == even_index:
    if odd_second:
      odd = odd_second
    elif even_second:
      even = even_second
  if odd is None and node.node_type & _NodeType.ODD:
    odd = node.index
  if even is None and node.node_type & _NodeType.EVEN:
    even = node.index
  odd_even_pairs[node.index] = (odd, even)

def _compute_depth_in_d_tree(k, depth_in_d_tree, d_links):
  if k not in depth_in_d_tree:
    if k in d_links:
      _compute_depth_in_d_tree(d_links[k], depth_in_d_tree, d_links)
      depth_in_d_tree[k] = depth_in_d_tree[d_links[k]] + 1
    else:
      depth_in_d_tree[k] = 0

def _merge_suffix_arrays(
    A_To, A_Te, LCP_To, LCP_Te, lca, text, depth_in_d_tree):
  A_T, LCP_T = [], []
  i, j, o, e = 0, 0, 0, 0
  while i < len(A_To) or j < len(A_Te):
    if i < len(A_To) and j < len(A_Te):
      lcp = depth_in_d_tree[lca.query(A_To[i], A_Te[j])]
      if text[lcp + A_To[i] - 1] <= text[lcp + A_Te[j] - 1]:
        A_T.append(A_To[i])
        i += 1
      else:
        A_T.append(A_Te[j])
        j += 1
    elif i < len(A_To):
      A_T.append(A_To[i])
      i += 1
    else:
      A_T.append(A_Te[j])
      j += 1
  for i in range(len(A_T) - 1):
    if A_T[i] % 2 == 1 and A_T[i + 1] % 2 == 1:
      o += A_To[o:].index(A_T[i])
      LCP_T.append(LCP_To[o])
    elif A_T[i] % 2 == 0 and A_T[i + 1] % 2 == 0:
      e += A_Te[e:].index(A_T[i])
      LCP_T.append(LCP_Te[e])
    else:
      LCP_T.append(depth_in_d_tree[lca.query(A_T[i], A_T[i + 1])])
  return A_T, LCP_T

def _extend_text(text, symbol):
  length = 2 ** math.ceil(math.log2(len(text) + 1))
  padding = length - len(text)
  return text + [symbol] * (padding - 1) + [symbol + 1], padding

def build_suffix_tree(text):
  text, padding = _extend_text([ord(c) + 1 for c in text[1:]], 0)
  A_T, LCP_T = _get_suffix_tree(text)
  return A_T[padding:], LCP_T[padding:]

def _get_suffix_tree(text):
  if len(text) == 1:
    return [1], [0]
  root, leaf = trie.TrieNode(''), trie.TrieNode(text[0:])
  root.node_type, leaf.node_type = _NodeType.NONE, _NodeType.NONE
  root.add_child(leaf)
  To, A_To, LCP_To = _get_odd_suffix_tree(text)
  Te, A_Te, LCP_Te = _get_even_suffix_tree(text, To, A_To)

  Tovermerged = _get_faulty_merge(To, Te, len(text))
  Tovermerged.odd_even_pairs = {}
  _initialise_odd_even_pairs_recurse(
      Tovermerged, len(text), Tovermerged.odd_even_pairs)
  lca = LCA(Tovermerged)
  Tovermerged.d_links = {
      k: lca.query(o + 1, e + 1)
      for k, (o, e) in Tovermerged.odd_even_pairs.items()
      if o and e and k != len(text) + 1 and o < len(text) and e < len(text)}
  Tovermerged.depth_in_d_tree = {root: 0}
  for pair in Tovermerged.odd_even_pairs:
    _compute_depth_in_d_tree(
        pair, Tovermerged.depth_in_d_tree, Tovermerged.d_links)

  return _merge_suffix_arrays(
      A_To, A_Te, LCP_To, LCP_Te, lca, text, Tovermerged.depth_in_d_tree)

def _set_index(new_node, old_node, n):
  if old_node.index <= n:
    new_node.index = old_node.index
  else:
    new_node.index = _get_faulty_merge_recurse.next_index
    _get_faulty_merge_recurse.next_index += 1

def _create_node(parent, other, node_type, n):
  new_node = trie.TrieNode(other.label)
  new_node.node_type = node_type
  _set_index(new_node, other, n)
  parent.add_child(new_node)
  return new_node

def _get_faulty_merge_recurse(node, odd, even, n):
  if node.parent is None:
    node.index = n + 1
  # Listy posortowane w kolejnosci: odd, even, wyjscie
  o_children = sorted(odd.children.items())
  e_children = sorted(even.children.items())
  i, j = 0, 0
  while i < len(o_children) or j < len(e_children):
    o_char, o_child = o_children[i] if i < len(o_children) else (None, None)
    e_char, e_child = e_children[j] if j < len(e_children) else (None, None)

    empty_node = trie.TrieNode('')
    empty_node.node_type = _NodeType.NONE
    if i == len(o_children):
      new_node = _create_node(node, e_child, _NodeType.EVEN, n)
      _get_faulty_merge_recurse(new_node, empty_node, e_child, n)
      j += 1
    elif j == len(e_children) or o_char < e_char:
      new_node = _create_node(node, o_child, _NodeType.ODD, n)
      _get_faulty_merge_recurse(new_node, o_child, empty_node, n)
      i += 1
    elif o_char == e_char:
      if len(e_child.label) > len(o_child.label):
        new_node = _create_node(node, o_child, _NodeType.ODD, n)
        split_node = sufftree.break_node(even, e_child, len(o_child.label))
        split_node.node_type = _NodeType.NONE
        _get_faulty_merge_recurse(new_node, o_child, split_node, n)
      elif len(e_child.label) < len(o_child.label):
        new_node = _create_node(node, e_child, _NodeType.EVEN, n)
        split_node = sufftree.break_node(odd, o_child, len(e_child.label))
        split_node.node_type = _NodeType.NONE
        _get_faulty_merge_recurse(new_node, split_node, e_child, n)
      else:
        new_node = _create_node(
            node, o_child if e_child.index > n else e_child, _NodeType.BOTH, n)
        _get_faulty_merge_recurse(new_node, o_child, e_child, n)
      i, j = i + 1, j + 1
    else:
      new_node = _create_node(node, e_child, _NodeType.EVEN, n)
      _get_faulty_merge_recurse(new_node, empty_node, e_child, n)
      j += 1

def _get_faulty_merge(To, Te, n):
  root = trie.TrieNode('')
  root.node_type = _NodeType.NONE
  _get_faulty_merge_recurse.next_index = n + 2
  _get_faulty_merge_recurse(root, To, Te, n)
  return root

def _substitute_with_ranks(S):
  ranks = {v: i + 1 for i, v in enumerate(radix_sort(list(set(S))))}
  return [ranks[c] for c in S]

def _get_odd_suffix_tree(text):
  S = _substitute_with_ranks(
      list((u, v) for u, v in zip(text[::2], text[1::2])))
  A_TS, LCP_TS = _get_suffix_tree(S)
  A_To = [2 * A_TS[i] - 1 for i in range(len(text) // 2)]
  LCP_To = [
      2 * lcp + (1 if text[u - 1 + 2 * lcp] == text[v - 1 + 2 * lcp] else 0)
      for u, v, lcp in zip(A_To, A_To[1:], LCP_TS)]
  To = sufftree.from_suffix_array_and_lcp(A_To, LCP_To, text, len(text) - 1)
  return To, A_To, LCP_To

def _get_even_suffix_tree(text, To, A_To):
  S = radix_sort(
      [(text[v - 2], v) for v in A_To if v > 1] + [(text[-1], len(text) + 1)],
      1)
  A_Te, lca = [t[1] - 1 for t in S], LCA(To)
  LCP_Te = [
      lca.query_depth(u + 1, v + 1) + 1 if text[u - 1] == text[v - 1] else 0
      for u, v in zip(A_Te, A_Te[1:])]
  Te = sufftree.from_suffix_array_and_lcp(A_Te, LCP_Te, text, len(text) - 1)
  return Te, A_Te, LCP_Te

def suffix_tree(text, n):
  A_T, LCP_T = build_suffix_tree(text)
  A_T.append(n + 1)
  LCP_T.append(0)
  T = sufftree.from_suffix_array_and_lcp(
      A_T, LCP_T, text[1:] + '$', len(text))
  return T, None

def suffix_array(text, n):
  A_T = build_suffix_tree(text)[0]
  A_T.insert(0, n + 1)
  return A_T

def lcp_array(text, _):
  LCP_T = build_suffix_tree(text)[1]
  LCP_T.insert(0, 0)
  LCP_T.insert(0, -1)
  return LCP_T
