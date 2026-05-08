from common import trie

def break_node(parent, child, index):
  u = trie.TrieNode(child.label[:index])
  child.label = child.label[index:]
  u.add_child(child)
  parent.add_child(u)
  return u

def _fast_find(v, w, split):
  index = 0
  while index < len(w) and w[index] in v.children:
    child = v.children[w[index]]
    if index + len(child.label) > len(w):
      return (
          break_node(v, child, len(w) - index) if split else v), len(w) - index
    v, index = child, index + len(child.label)
  return v, len(w) - index

def _slow_find(v, w):
  index = 0
  while index < len(w) and w[index] in v.children:
    child = v.children[w[index]]
    for i, c in enumerate(child.label):
      if w[index + i] != c:
        return break_node(v, child, i), len(w) - (index + i)
    v, index = child, index + len(child.label)
  return v, len(w) - index

def naive(t, n):
  t += '$'
  root, leaf = trie.TrieNode(''), trie.TrieNode(t[1:])
  root.add_child(leaf)
  for i in range(2, n + 2):
    head, remaining = _slow_find(root, t[i:])
    leaf = trie.TrieNode(t[-remaining:])
    head.add_child(leaf)
  return root

def weiner(t, n):
  t += '$'
  root = trie.TrieNode('')
  link, head = { (root, ''): root }, root
  for i in range(n + 1, 0, -1):
    # invariant: link[v][c] = u for u, v with w(u) = c w(v)
    v, depth = head, n + 2
    while v != root and link.get((v, t[i])) is None:
      v, depth = v.parent, depth - len(v.label)
    u = link.get((v, t[i]))
    if u is None or t[depth] in u.children:
      if u is None:
        u, remaining = _slow_find(root, t[depth - 1:])
      else:
        u, remaining = _slow_find(u, t[depth:])
      v, _ = _fast_find(v, t[depth:-remaining], False)
      depth = len(t) - remaining
      if u != root:
        link[(v, t[i])] = u
    leaf = trie.TrieNode(t[depth:])
    u.add_child(leaf)
    head = leaf
  return root, link

def mccreight(t, n):
  t += '$'
  root, leaf = trie.TrieNode(''), trie.TrieNode(t[1:])
  root.add_child(leaf)
  S, head = { }, root
  for _ in range(2, n + 2):
    # invariant: S[v] is defined for all v != head(i - 1)
    if head == root:
      # exception 1: tree with one leaf
      beta, gamma, v = '', head.children[leaf.label[0]].label[1:], root
    else:
      if head.parent == root:
        # exception 2: head.parent is a root
        beta = head.parent.children[head.label[0]].label[1:]
      else:
        beta = head.parent.children[head.label[0]].label
      gamma = head.children[leaf.label[0]].label
      v, _ = _fast_find(S[head.parent], beta, split = True)
    S[head] = v
    head, remaining = _slow_find(v, gamma)
    leaf = trie.TrieNode(t[-remaining:])
    head.add_child(leaf)
  return root, S

def ukkonen(t, n):
  t += '$'
  root, leaf = trie.TrieNode(''), trie.TrieNode(t[1:])
  root.add_child(leaf)
  S, head, shift = {root : root}, root, 0
  for i in range(2, n + 2):
    # invariant: S[v] is defined for all v != head(i - 1)
    child = head.children.get(t[i - shift])
    if (child is None or shift >= len(child.label)
        or t[i] != child.label[shift]):
      previous_head = None
      while shift > 0 or t[i] not in head.children:
        v = (break_node(head, head.children[t[i - shift]], shift)
             if shift > 0 else head)
        v.add_child(trie.TrieNode(t[i:]))
        if head == root:
          shift -= 1
        if previous_head is not None:
          S[previous_head] = v
        previous_head, head = v, S[head]
        if shift > 0:
          head, shift = _fast_find(head, t[i - shift:i], split = False)
      if previous_head is not None:
        S[previous_head] = head
      child = head.children.get(t[i - shift]) if shift >= 0 else None
    if child is not None and len(child.label) == shift + 1:
      head, shift = head.children[t[i - shift]], 0
    else:
      shift += 1
  return root, S

def from_suffix_array_and_lcp(SA, LCP, t, n):
  root, leaf = trie.TrieNode(''), trie.TrieNode(t[SA[0] - 1:])
  root.set_depth(0)
  root.add_child(leaf)
  leaf.set_depth(len(leaf.label))
  root.index, leaf.index = n + 2, n + 2 - leaf.depth

  next_index, last_node = root.index + 1, leaf
  for a, lcp in zip(SA[1:], LCP):
    suffix = t[a - 1:]
    current_node = last_node
    while current_node.depth > lcp:
      current_node = current_node.parent
    if current_node.depth == lcp:
      if current_node.depth == len(suffix):
        new_node = current_node
      else:
        new_node = trie.TrieNode(suffix[current_node.depth:])
        current_node.add_child(new_node)
    else:
      rightmost_child = max(current_node.children.items())[1]
      split_node = break_node(
          current_node, rightmost_child, lcp - current_node.depth)
      split_node.set_depth(lcp)
      if suffix[lcp:]:
        new_node = trie.TrieNode(suffix[lcp:])
        split_node.add_child(new_node)
        split_node.index = next_index
        next_index += 1
      else:
        new_node = split_node
    new_node.index = n + 2 - len(suffix)
    new_node.set_depth(len(suffix))
    last_node = new_node
  return root

def contains(ST, _, w, n, m):
  ST.set_depth()
  v = ST.find_node(w[1:], m)
  yield from sorted(
      v.get_all_leaves(lambda x: n + 2 - x.depth)) if v is not None else []
