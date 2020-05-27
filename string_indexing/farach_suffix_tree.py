from operator import itemgetter

from common import trie
from common.lca import LCA
from string_indexing import suffix_tree

# takes A - array of tuples and sorts it stably according to ind index in tuple
def counting_sort(A, ind):
  n = max(max(A, key=itemgetter(0))[0], max(A, key=itemgetter(1))[1],
          len(A)) + 1
  result = [0] * len(A)
  count = [0] * n
  for tp in A:
    count[tp[ind]] += 1
  for i in range(1, n):
    count[i] += count[i - 1]
  for i in reversed(range(len(A))):
    count[A[i][ind]] -= 1
    result[count[A[i][ind]]] = A[i]
  for i, value in enumerate(result):
    A[i] = value


def radix_sort(A, upper_index=2):
  for i in reversed(range(upper_index)):
    counting_sort(A, i)


# for every node c that has both odd and even descendants, find pair (a,
# b) such that a and b are descendants of c,
# a is odd, b is even and LCA(a,b) = c
def initialise_odd_even_pairs(root, n):
  setattr(root, "odd_even_pairs", {})
  initialise_odd_even_pairs_rec(root, n, getattr(root, "odd_even_pairs"))


def initialise_odd_even_pairs_rec(node, n, odd_even_pairs):
  if not node.children:
    odd = even = -1
    if hasattr(node, "odd"):
      odd = node.index
    if hasattr(node, "even"):
      even = node.index
    odd_even_pairs[node.index] = (odd, even)
    return

  for child in node.children.values():
    initialise_odd_even_pairs_rec(child, n, odd_even_pairs)
  odd1 = odd2 = even1 = even2 = -1
  odd1_ind = even1_ind = -1
  for child in node.children.values():
    o, e = odd_even_pairs[child.index]
    if o != -1:
      if odd1 == -1:
        odd1 = o
        odd1_ind = child.index
      elif odd2 == -1:
        odd2 = o
    if e != -1:
      if even1 == -1:
        even1 = e
        even1_ind = child.index
      elif even2 == -1:
        even2 = e
  odd = odd1
  even = even1
  if odd1_ind == even1_ind:
    if odd2 != -1:
      odd = odd2
    elif even2 != -1:
      even = even2
  if odd == -1 and hasattr(node, "odd"):
    odd = node.index
  if even == -1 and hasattr(node, "even"):
    even = node.index
  odd_even_pairs[node.index] = (odd, even)

def compute_d_links(lca, n, root):
  setattr(root, "d_links", {})
  d_links = getattr(root, "d_links")
  odd_even_pairs = getattr(root, "odd_even_pairs")
  for k, (o, e) in odd_even_pairs.items():
    if o != -1 and e != -1 and k != n + 1:
      if o + 1 <= n and e + 1 <= n:
        d_links[k] = lca.query(o + 1, e + 1)


def compute_depth_in_d_tree(k, depth_in_d_tree, d_links):
  if k not in depth_in_d_tree:
    if k in d_links:
      compute_depth_in_d_tree(d_links[k], depth_in_d_tree, d_links)
      depth_in_d_tree[k] = depth_in_d_tree[d_links[k]] + 1
    else:
      depth_in_d_tree[k] = 0


def compute_depths_in_d_tree(root):
  setattr(root, "depth_in_d_tree", {root: 0})
  depth_in_d_tree = getattr(root, "depth_in_d_tree")
  odd_even_pairs = getattr(root, "odd_even_pairs")
  d_links = getattr(root, "d_links")
  for k in odd_even_pairs:
    compute_depth_in_d_tree(k, depth_in_d_tree, d_links)


# merge odd and even suffix arrays, using longest common prefix between odd
# and even suffixes
# longest common prefix of odd and even suffix is computed as lca query on
# overmerged odd and even trees
def merge_suffix_arrays(A_To, A_Te, LCP_To, LCP_Te, lca, text, depth_in_d_tree):
  A_T = []
  LCP_T = []
  i = j = 0
  while i < len(A_To) or j < len(A_Te):
    if i < len(A_To) and j < len(A_Te):
      lcp = depth_in_d_tree[lca.query(A_To[i], A_Te[j])]
      if text[lcp + A_To[i] - 1] <= text[lcp + A_Te[j] - 1]:
        A_T.append(A_To[i])
        i += 1
      else:
        A_T.append(A_Te[j])
        j += 1
    else:
      if i < len(A_To):
        A_T.append(A_To[i])
        i += 1
      else:
        A_T.append(A_Te[j])
        j += 1
  o = e = 0
  for i in range(len(A_T) - 1):
    if A_T[i] % 2 == 1 and A_T[i + 1] % 2 == 1:
      while A_To[o] != A_T[i]:
        o += 1
      LCP_T.append(LCP_To[o])
    elif A_T[i] % 2 == 0 and A_T[i + 1] % 2 == 0:
      while A_Te[e] != A_T[i]:
        e += 1
      LCP_T.append(LCP_Te[e])
    else:
      LCP_T.append(depth_in_d_tree[lca.query(A_T[i], A_T[i + 1])])
  return A_T, LCP_T


# append symbol as many times as necessary to make the text length equal some
# closest power of two greater than original
# length
def extend_text(text, symbol):
  length = 1
  while length <= len(text):
    length *= 2
  n = len(text)
  if length > n:
    for _ in range(length - n - 1):
      text.append(symbol)
    text.append(symbol + 1)



# runs Farach's algorithm on extended text and then discards extra nodes /
# array entries related to extra symbols added
# at the end of text; finally returns these structures for the original text
# handles both normal strings (starting with '#') and strings over integer
# alphabet
def build_suffix_tree(text):
  if text[0] == '#':
    text = text.replace('#', '')
    text = [ord(i) + 1 for i in text]
  else:
    text = [i + 1 for i in text]
  n = len(text)
  extend_text(text, 0)
  T, A_T, LCP_T = get_suffix_tree(text)
  k = len(text) - n
  A_T = A_T[k:]
  LCP_T = LCP_T[k:]
  T = suffix_and_lcp_array_to_tree(A_T, LCP_T, text[:n])
  return T, A_T, LCP_T


# function created to ensure compatibility with already existing tests
def farach_suffix_tree(text, n):
  T, A_T, LCP_T = build_suffix_tree(text)
  A_T.append(len(text))
  LCP_T.append(0)
  text = text.replace('#', '')
  T = suffix_and_lcp_array_to_tree(A_T, LCP_T, text + '$')
  return T, None


# function created to ensure compatibility with already existing tests
def farach_suffix_array(text, n):
  A_T = build_suffix_tree(text)[1]
  A_T.insert(0, n + 1)
  return A_T


# function created to ensure compatibility with already existing tests
def farach_lcp_array(text, n):
  LCP_T = build_suffix_tree(text)[2]
  LCP_T.insert(0, 0)
  LCP_T.insert(0, -1)
  return LCP_T


# main function in Farach's algorithm; builds odd, even suffix trees and
# merges them into correct suffix tree of the
# entire text
def get_suffix_tree(text):
  root, leaf = trie.TrieNode(''), trie.TrieNode(text[0:])
  root.add_child(leaf)
  if len(text) == 1:
    return root, [1], [0]
  (To, A_To, LCP_To) = get_odd_suffix_tree(text)
  (Te, A_Te, LCP_Te) = get_even_suffix_tree(text, To, A_To)
  Tovermerged = get_faulty_merge(To, Te, text)
  initialise_odd_even_pairs(Tovermerged, len(text))
  lca = LCA()
  lca.preprocess(Tovermerged)
  compute_d_links(lca, len(text), Tovermerged)
  compute_depths_in_d_tree(Tovermerged)
  A_T, LCP_T = merge_suffix_arrays(A_To, A_Te, LCP_To, LCP_Te, lca, text,
                                   getattr(Tovermerged, "depth_in_d_tree"))
  T = suffix_and_lcp_array_to_tree(A_T, LCP_T, text)
  return T, A_T, LCP_T


# recursive method called for every node, used to create overmerge odd and
# even suffix trees
# preserves node indices from odd and even trees; adds other indices to other
# nodes
# this way, if some node nd has index i from 1 to len(text), it means that
# word(nd) is a suffix of text starting at i
def get_faulty_merge_recurse(node, odd, even, text):
  def set_index(new_nd, old_nd):
    n = len(text)
    if old_nd.index <= n:
      new_nd.index = old_nd.index
    else:
      new_nd.index = get_faulty_merge_recurse.next_index
      get_faulty_merge_recurse.next_index += 1

  if node.parent is None:
    node.index = len(text) + 1
  i = 0
  j = 0
  # two following lines won't work linear, but for clarity, they are written
  # this way
  # Farach's algorithm works on lists which are already sorted in odd,
  # even and resulting tree, but current API uses
  # dictionary to represent children set and hence the call to 'sorted'
  # function; if we used list instead of dict,
  # we would simply omit them
  o_children = sorted(odd.children.items())
  e_children = sorted(even.children.items())
  while i < len(o_children) or j < len(e_children):
    o_child = e_child = o_char = e_char = None
    if i < len(o_children):
      o_child = o_children[i][1]
      o_char = o_children[i][0]
    if j < len(e_children):
      e_child = e_children[j][1]
      e_char = e_children[j][0]

    if i == len(o_children):
      new_node = trie.TrieNode(e_child.label)
      set_index(new_node, e_child)
      node.add_child(new_node)
      setattr(new_node, "even", True)
      get_faulty_merge_recurse(new_node, trie.TrieNode(""), e_child, text)
      j += 1
      continue
    if j == len(e_children):
      new_node = trie.TrieNode(o_child.label)
      set_index(new_node, o_child)
      node.add_child(new_node)
      setattr(new_node, "odd", True)
      get_faulty_merge_recurse(new_node, o_child, trie.TrieNode(""), text)
      i += 1
      continue

    if o_char == e_char:
      o_len = len(o_child.label)
      e_len = len(e_child.label)
      if o_len != e_len:
        odd_shorter, short_label = (True, o_child.label) if e_len > o_len else (
            False, e_child.label)
        new_node = trie.TrieNode(short_label)
        node.add_child(new_node)
        if odd_shorter:
          setattr(new_node, "odd", True)
          set_index(new_node, o_child)
        else:
          setattr(new_node, "even", True)
          set_index(new_node, e_child)
        # add new artificial node in even or odd tree to recurse properly
        if odd_shorter:
          split_node = suffix_tree.break_node(even, e_child, o_len)
          get_faulty_merge_recurse(new_node, o_child, split_node, text)
        else:
          split_node = suffix_tree.break_node(odd, o_child, e_len)
          get_faulty_merge_recurse(new_node, split_node, e_child, text)
      else:  # o_len == e_len and o_char == e_char
        new_node = trie.TrieNode(o_child.label)
        set_index(new_node, e_child if e_child.index <= len(text) else o_child)
        node.add_child(new_node)
        setattr(new_node, "odd", True)
        setattr(new_node, "even", True)
        get_faulty_merge_recurse(new_node, o_child, e_child, text)
      i += 1
      j += 1
    else:
      if o_char < e_char:
        new_node = trie.TrieNode(o_child.label)
        set_index(new_node, o_child)
        node.add_child(new_node)
        get_faulty_merge_recurse(new_node, o_child, trie.TrieNode(""), text)
        i += 1
        setattr(new_node, "odd", True)
      else:
        new_node = trie.TrieNode(e_child.label)
        set_index(new_node, e_child)
        node.add_child(new_node)
        get_faulty_merge_recurse(new_node, trie.TrieNode(""), e_child, text)
        j += 1
        setattr(new_node, "even", True)


# returns an overmerged tree of To and Te - odd and even suffix trees
def get_faulty_merge(To, Te, text):
  root = trie.TrieNode('')
  get_faulty_merge_recurse.next_index = len(text) + 2
  get_faulty_merge_recurse(root, To, Te, text)
  return root


# creates in linear time the suffix tree of text using A and LCP arrays
# algorithm implemented based on
# https://en.wikipedia.org/wiki/LCP_array#Suffix_tree_construction
def suffix_and_lcp_array_to_tree(A, LCP, text):
  next_index = len(text) + 1
  n = len(A)
  root = trie.TrieNode('')
  leaf = trie.TrieNode(text[A[0] - 1:])
  root.set_depth(0)
  root.add_child(leaf)
  leaf.set_depth(len(leaf.label))
  leaf.index = len(text) + 1 - leaf.depth
  root.index = next_index
  next_index += 1

  lastNode = leaf
  for i in range(1, n):
    suffix = text[A[i] - 1:]
    currentNode = lastNode
    while currentNode.depth > LCP[i - 1]:
      currentNode = currentNode.parent
    if currentNode.depth == LCP[i - 1]:
      if currentNode.depth == len(suffix):
        newNode = currentNode
      else:
        newNode = trie.TrieNode(suffix[currentNode.depth:])
        currentNode.add_child(newNode)
    else:
      rightmostChild = \
      sorted(currentNode.children.items())[len(currentNode.children) - 1][1]
      splitNode = suffix_tree.break_node(currentNode, rightmostChild,
                                         LCP[i - 1] - currentNode.depth)
      splitNode.set_depth(LCP[i - 1])
      if len(suffix[LCP[i - 1]:]) >= 1:
        newNode = trie.TrieNode(suffix[LCP[i - 1]:])
        splitNode.add_child(newNode)
        splitNode.index = next_index
        next_index += 1
      else:
        newNode = splitNode
    newNode.index = len(text) - len(suffix) + 1
    newNode.set_depth(len(suffix))
    lastNode = newNode
  return root


def substitute_with_ranks(S):
  st = list(set(S))
  radix_sort(st)
  index_of = {st[i]: i + 1 for i in range(len(st))}
  S = [index_of[c] for c in S]
  return S


# returns suffix tree for odd suffixes of text
def get_odd_suffix_tree(text):
  n = len(text)
  S = substitute_with_ranks(
      [(text[i], text[i + 1]) for i in range(n) if i % 2 == 0])
  _, A_TS, LCP_TS = get_suffix_tree(S)
  A_To, LCP_To = [], []
  for i in range(n // 2):
    A_To.append(2 * A_TS[i] - 1)
  for i in range(n // 2 - 1):
    if text[A_To[i] - 1 + 2 * LCP_TS[i]] == text[
        A_To[i + 1] - 1 + 2 * LCP_TS[i]]:
      LCP_To.append(2 * LCP_TS[i] + 1)
    else:
      LCP_To.append(2 * LCP_TS[i])
  To = suffix_and_lcp_array_to_tree(A_To, LCP_To, text)
  return To, A_To, LCP_To


# returns suffix tree for even suffixes of text based on already created odd
# suffix tree and odd suffix array
def get_even_suffix_tree(text, To, A_To):
  S = [(text[A_To[i] - 2], A_To[i]) for i in range(len(A_To)) if A_To[i] > 1]
  S.append((text[-1], len(text) + 1))
  radix_sort(S, 1)
  A_Te, LCP_Te = [t[1] - 1 for t in S], []
  lca = LCA()
  lca.preprocess(To)
  for i in range(len(A_Te) - 1):
    if text[A_Te[i] - 1] == text[A_Te[i + 1] - 1]:
      LCP_Te.append(lca.query_depth(A_Te[i] + 1, A_Te[i + 1] + 1) + 1)
    else:
      LCP_Te.append(0)
  Te = suffix_and_lcp_array_to_tree(A_Te, LCP_Te, text)
  return Te, A_Te, LCP_Te
