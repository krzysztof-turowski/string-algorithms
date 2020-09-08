class AutomatonNode:
  def __init__(self, depth = 0):
    self.parent, self.children, self.fail = None, {}, None
    self.output, self.depth = [], depth

  def add_child(self, child, label):
    self.children[label] = child
    child.parent = self

class DawgNode:
  def __init__(self):
    self.primary, self.secondary, self.suffix = {}, {}, None

class DAWG:
  def __init__(self, patterns):
    self.root = DawgNode()
    for pattern in patterns:
      current_node = self.root
      for char in pattern:
        current_node = self.update(current_node, char)

  def update(self, node, label):
    if label in node.primary:
      return node.primary[label]
    if label in node.secondary:
      return self.split(node, node.secondary[label], label)
    next_node = DawgNode()
    node.primary[label] = next_node
    current_node, suffix_node = node, None
    while current_node is not self.root and suffix_node is None:
      current_node = current_node.suffix
      if label in current_node.primary:
        suffix_node = current_node.primary[label]
      elif label in current_node.secondary:
        child_node = current_node.secondary[label]
        suffix_node = self.split(current_node, child_node, label)
      else:
        current_node.secondary[label] = next_node
    if suffix_node is None:
      suffix_node = self.root
    next_node.suffix = suffix_node
    return next_node

  def split(self, parent_node, child_node, label):
    new_child = DawgNode()
    del parent_node.secondary[label]
    parent_node.primary[label] = new_child
    new_child.secondary = {**child_node.primary, **child_node.secondary}
    new_child.suffix = child_node.suffix
    child_node.suffix = new_child
    current_node = parent_node
    while current_node is not self.root:
      current_node = current_node.suffix
      for char, node in current_node.secondary.items():
        if node == child_node:
          current_node.secondary[char] = new_child
          break
      else:
        return new_child
    return new_child

  def traverse(self, text, p, q):
    node = self.root
    for i in range(q, p - 1, -1):
      if text[i] in node.primary:
        node = node.primary[text[i]]
      elif text[i] in node.secondary:
        node = node.secondary[text[i]]
      else:
        return text[i + 1:q + 1]
    return text[p:q + 1]
