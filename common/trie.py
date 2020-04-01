class TrieNode:
  def __init__(self, w):
    self.label = w
    self.children = {}
    self.parent = None

  def add_child(self, child):
    self.children[child.label[0]] = child
    child.parent = self

  def contains(self, word, m):
    if m == 0:
      return True
    if word[0] not in self.children:
      return False
    child = self.children[word[0]]
    if m <= len(child.label):
      return child.label.startswith(word)
    return word.startswith(child.label) and child.contains(word[len(child.label):], m - len(child.label))

  @staticmethod
  def compare(this, other):
    if this.label != other.label or this.children.keys() != other.children.keys():
      return False
    for key in this.children.keys():
      if not TrieNode.compare(this.children[key], other.children[key]):
        return False
    return True
