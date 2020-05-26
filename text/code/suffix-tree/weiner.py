def weiner(text, n):
  text = text + '$'
  root = trie.TrieNode("")
  link, head = { (root, ""): root }, root
  for i in range(n + 1, 0, -1):
    # niezmiennik: link[v][c] = u dla wewnętrznych u i v takich, że word(u) = c word(v)
    v, depth = head, n + 2
    while v != root and link.get((v, text[i])) is None:
      v, depth = v.parent, depth - len(v.label)
    u = link.get((v, text[i]))
    if u is None or text[depth] in u.children:
      if u is None:
        u, remaining = slow_find(root, text[depth - 1:])
      else:
        u, remaining = slow_find(u, text[depth:])
      v, _ = fast_find(v, text[depth:-remaining], False)
      depth = len(text) - remaining
      if u != root:
        link[(v, text[i])] = u
    leaf = trie.TrieNode(text[depth:])
    u.add_child(leaf)
    head = leaf
  return root, link
