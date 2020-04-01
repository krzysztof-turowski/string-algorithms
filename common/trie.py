class TrieNode:
  def __init__(self, w):
    self.label = w
    self.children = {}
    self.parent = None

  def add_child(self, child):
    self.children[child.label[0]] = child
    child.parent = self

  def contains(self, w):
    if len(w) == 0:
      return True
    if w[0] not in self.children:
      return False
    child = self.children[w[0]]
    if len(w) <= len(child.label):
      return w == child.label[:len(w)]
    return w[:len(child.label)] and child.contains(w[len(child.label):])

  @staticmethod
  def compare(this, other):
    if this.label != other.label or this.children.keys() != other.children.keys():
      return False
    for key in this.children.keys():
      if not TrieNode.compare(this.children[key], other.children[key]):
        return False
    return True
