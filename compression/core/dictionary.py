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
  def __init__(self, label, parent=None):
    self.label = label
    self.children = {}
    self.parent, self.link, self.terminal = self if parent is None else parent, self, None

  def insert(self, w, code):
    if not w:
      self.terminal = True
      self.label = code
      return self
    if w[0] not in self.children:
      child = TrieDict(-1, self)
      self.children[w[0]] = child
      return child.insert(w[1:], code)

    child = self.children[w[0]]
    return child.insert(w[1:], code)

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
    return self.link.parent.link

  def link(self, node):
    self.link = node
