# pylint: disable=too-many-instance-attributes
class TrieDict(object):
  def __init__(self, label, edge=None, depth=0, index=None, parent=None):
    self.children = {}
    self.link, self.terminal = None, None

    self.label = label
    self.edge = edge
    self.depth = depth
    self.index = index
    self.parent = self if parent is None else parent

  def insert(self, w, code, index=None):
    if not w:
      self.terminal = True
      self.label = code
      self.index = index
      return self
    if w[0] not in self.children:
      child = TrieDict(-1, w[0], self.depth + 1, index, self)
      self.children[w[0]] = child
      return child.insert(w[1:], code, index)

    child = self.children[w[0]]
    return child.insert(w[1:], code, index)

  def search(self, w):
    if not w:
      return self
    if w[0] not in self.children:
      return None
    child = self.children[w[0]]
    return child.search(w[1:])

  def extend(self, c):
    if c not in self.children:
      return None
    return self.children[c]

  def contract(self):
    current = self.link.parent
    while current.parent != current and current.link is None:
      current = current.parent
    return current.link

  def connect(self, node):
    self.link = node

# pylint: disable=no-self-use
class TrieReverseTrie(object):
  def __init__(self):
    self.trie = TrieDict(None, index=0)
    self.trie_rev = TrieDict(None, index=0)
    self.size = 0

    self.trie.connect(self.trie_rev)
    self.trie_rev.connect(self.trie)

  def insert(self, node, w, wr, code):
    self.size += 1
    new_node = node.insert(w, code, self.size)
    new_node_rev = self.trie_rev.insert(wr, code, self.size)
    new_node.connect(new_node_rev)
    new_node_rev.connect(new_node)
    return new_node

  def search(self, w):
    return self.trie.search(w)

  def get_prefix(self, node):
    prefix = ""
    while node.parent != node:
      prefix += node.edge
      node = node.parent
    return prefix[::-1]
