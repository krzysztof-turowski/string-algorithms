class TrieNode:
  def __init__(self, w):
    self.label = w
    self.children = {}
    self.parent, self.depth = None, None

  def add_child(self, child):
    self.children[child.label[0]] = child

  def get_all_leaves(self, f):
    if len(self.children) == 0:
      return [f(self)]
    return [value for _, child in sorted(self.children.items())
            for value in child.get_all_leaves(f)]

  def set_parent(self):
    for _, child in self.children.items():
      child.parent = self
      child.set_parent()

  def set_depth(self, depth = 0):
    self.depth = depth
    for _, child in self.children.items():
      child.set_depth(depth + len(child.label))

  def find_node(self, word, m):
    if m == 0:
      return self
    if word[0] not in self.children:
      return None
    child = self.children[word[0]]
    label = child.label
    if m < len(label):
      return child if child.label.startswith(word) else None
    return child.find_node(word[len(label):], m - len(label)) if word.startswith(label) else None

  @staticmethod
  def compare(this, other):
    if this.label != other.label or this.children.keys() != other.children.keys():
      return False
    for key in this.children.keys():
      if not TrieNode.compare(this.children[key], other.children[key]):
        return False
    return True
