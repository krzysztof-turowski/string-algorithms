from common import trie

def break_node(parent, child, index):
  u = trie.TrieNode(child.label[:index])
  child.label = child.label[index:]
  u.add_child(child)
  parent.add_child(u)
  return u

def fast_find(v, w):
  index = 0
  while index < len(w) and w[index] in v.children:
    child = v.children[w[index]]
    if index + len(child.label) > len(w):
      return break_node(v, child, len(w) - index)
    v, index = child, index + len(child.label)
  return v

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
      v = fast_find(S[head.parent], beta)
    S[head] = v
    head, remaining = slow_find(v, gamma)
    leaf = trie.TrieNode(text[-remaining:])
    head.add_child(leaf)
  return root
