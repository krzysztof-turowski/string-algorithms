class TrieNode:
  def __init__(self, w):
    self.label = w
    self.children = {}
    self.parent = None

  def add_child(self, child):
    self.children[child.label[0]] = child
    child.parent = self

  @staticmethod
  def compare(this, other):
    if this.label != other.label or this.children.keys() != other.children.keys():
      return False
    for key in this.children.keys():
      if not TrieNode.compare(this.children[key], other.children[key]):
        return False
    return True
