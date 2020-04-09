from common import trie

def break_node(parent, child, index):
  u = trie.TrieNode(child.label[:index])
  child.label = child.label[index:]
  u.add_child(child)
  parent.add_child(u)
  return u

def fast_find(v, w, split):
  index = 0
  while index < len(w) and w[index] in v.children:
    child = v.children[w[index]]
    if index + len(child.label) > len(w):
      return (break_node(v, child, len(w) - index) if split else v), len(w) - index
    v, index = child, index + len(child.label)
  return v, len(w) - index

def slow_find(v, w):
  index = 0
  while index < len(w) and w[index] in v.children:
    child = v.children[w[index]]
    for i, c in enumerate(child.label):
      if w[index + i] != c:
        return break_node(v, child, i), len(w) - (index + i)
    v, index = child, index + len(child.label)
  return v, len(w) - index

def naive(text, n):
  text = text + '$'
  root, leaf = trie.TrieNode(""), trie.TrieNode(text[1:])
  root.add_child(leaf)
  for i in range(2, n + 2):
    head, remaining = slow_find(root, text[i:])
    leaf = trie.TrieNode(text[-remaining:])
    head.add_child(leaf)
  return root

def weiner(text, n):
  text = text + '$'
  root = trie.TrieNode("")
  link, head = { }, root
  for i in range(n + 1, 0, -1):
    # niezmiennik: link[v][c] = u jest zdefiniowane zawsze gdy word(u) = c word(v)
    v, depth = head, -1
    while v != root and link.get((v, text[i])) is None:
      v, depth = v.parent, depth - len(v.label)
    u = link.get((v, text[i])) if v != root else root
    if text[i] in u.children:
      v, shift = slow_find(u, text[depth:])
      depth = -shift
    leaf = trie.TrieNode(text[depth:])
    v.add_child(leaf)
    link[(head, text[i])] = leaf
    head = leaf
  return root, link

def mccreight(text, n):
  text = text + '$'
  root, leaf = trie.TrieNode(""), trie.TrieNode(text[1:])
  root.add_child(leaf)
  S, head = { }, root
  for _ in range(2, n + 2):
    # niezmiennik: S[v] jest zdefiniowane dla wszystkich v != head(i - 1)
    if head == root:
      # wyjątek 1: drzewo z jednym liściem
      beta, gamma, v = "", head.children[leaf.label[0]].label[1:], root
    else:
      if head.parent == root:
        # wyjątek 2: head.parent jest rootem
        beta = head.parent.children[head.label[0]].label[1:]
      else:
        beta = head.parent.children[head.label[0]].label
      gamma = head.children[leaf.label[0]].label
      v, _ = fast_find(S[head.parent], beta, split = True)
    S[head] = v
    head, remaining = slow_find(v, gamma)
    leaf = trie.TrieNode(text[-remaining:])
    head.add_child(leaf)
  return root, S

def ukkonen(text, n):
  text = text + '$'
  root, leaf = trie.TrieNode(""), trie.TrieNode(text[1:])
  root.add_child(leaf)
  S, head, shift = {root : root}, root, 0
  for i in range(2, n + 2):
    # niezmiennik: S[v] jest zdefiniowane dla wszystkich v != head(i - 1)
    child = head.children.get(text[i - shift])
    if child is None or shift >= len(child.label) or text[i] != child.label[shift]:
      previous_head = None
      while shift > 0 or text[i] not in head.children:
        v = break_node(head, head.children[text[i - shift]], shift) if shift > 0 else head
        v.add_child(trie.TrieNode(text[i:]))
        if head == root:
          shift -= 1
        if previous_head is not None:
          S[previous_head] = v
        previous_head, head = v, S[head]
        if shift > 0:
          head, shift = fast_find(head, text[i - shift:i], split = False)
      if previous_head is not None:
        S[previous_head] = head
      child = head.children.get(text[i - shift]) if shift >= 0 else None
    if child is not None and len(child.label) == shift + 1:
      head, shift = head.children[text[i - shift]], 0
    else:
      shift += 1
  return root, S

def contains(ST, _, word, n, m):
  ST.set_depth()
  v = ST.find_node(word[1:], m)
  yield from sorted(v.get_all_leaves(lambda x: n + 2 - x.depth)) if v is not None else []
