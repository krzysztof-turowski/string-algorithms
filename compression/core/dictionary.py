class SimpleDict:
  """ Simple dict """
  def __init(self):
      self.dict = {}

  def insert(self, w, code):
    self.dict[w] = code

  def search(self, w):
    return self.dict[w]


class TrieDict:
  """ Powerful dict """
  def __init__(self, label, edge=None, depth=0, index=None, parent=None):
    self.label = label
    self.edge = edge
    self.children = {}
    self.parent, self.link, self.terminal = self if parent is None else parent, None, None
    self.depth = depth
    self.index = index

  def insert(self, w, code, index=None):
    if not w:
      self.terminal = True
      self.label = code
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
