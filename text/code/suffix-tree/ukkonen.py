def ukkonen(text, n):
  text = text + '$'
  root, leaf = trie.TrieNode(''), trie.TrieNode(text[1:])
  root.add_child(leaf)
  S, head, shift = {root : root}, root, 0
  for i in range(2, n + 2):
    # niezmiennik: S[v] jest zdefiniowane dla wszystkich v != head(i - 1)
    child = head.children.get(text[i - shift])
    if (child is None or shift >= len(child.label)
        or text[i] != child.label[shift]):
      previous_head = None
      while shift > 0 or text[i] not in head.children:
        v = (break_node(head, head.children[text[i - shift]], shift)
             if shift > 0 else head)
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
