from queue import Queue

class _AhoCorasickNode:
  def __init__(self, depth=0):
    self.edges = {}
    self.final = []
    self.fail = None
    self.depth = depth

class _AhoCorasickMachine:
  def __init__(self, patterns):
    self.root = None
    self.create_aho_corasick_machine(patterns)

  def create_trie(self, patterns):
    self.root = _AhoCorasickNode()
    for pattern in patterns:
      current_node = self.root
      for char in pattern:
        new_node = _AhoCorasickNode(current_node.depth + 1)
        current_node = current_node.edges.setdefault(char, new_node)
      current_node.final.append(pattern)

  def create_aho_corasick_machine(self, patterns):
    self.create_trie(patterns)
    queue = Queue()
    for node in self.root.edges.values():
      queue.put(node)
      node.fail = self.root
    while not queue.empty():
      cur_node = queue.get()
      for label, next_node in cur_node.edges.items():
        queue.put(next_node)
        fail_node = cur_node.fail
        while fail_node is not None and not label in fail_node.edges:
          fail_node = fail_node.fail
        next_node.fail = fail_node.edges[label] if fail_node else self.root
        next_node.final += next_node.fail.final

  def step(self, node, label):
    while not label in node.edges and node is not self.root:
      node = node.fail
    return node.edges[label] if label in node.edges else self.root

  def traverse(self, text):
    node = self.root
    for char in text:
      node = self.step(node, char)
    return node

class DawgNode:
  def __init__(self):
    self.primary = {}
    self.secondary = {}
    self.suffix = None

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

  @staticmethod
  def traverse(node, text, p, q):
    for i in range(q, p - 1, -1):
      if text[i] in node.primary:
        node = node.primary[text[i]]
      elif text[i] in node.secondary:
        node = node.secondary[text[i]]
      else:
        return text[i+1: q+1]
    return text[p:q+1]

def build(W):
  class Utils:
    def __init__(self, W):
      self.acm = _AhoCorasickMachine(W)
      self.dawg = DAWG([pattern[::-1] for pattern in W])
      self.m = min(len(x) for x in W)
  return Utils(W)

def search(text, n, S):
  def _next1(S, gamma, char):
    return S.acm.step(gamma, char)
  def _next2(S, text, crit_pos, i):
    return S.acm.traverse(S.dawg.traverse(S.dawg.root, text, crit_pos, i))
  i, gamma = 0, S.acm.root
  while True:
    while gamma.depth >= S.m/2:
      if gamma.final:
        for match in gamma.final:
          yield (match, i - len(match) + 1)
      i += 1
      if i > n:
        return
      gamma = _next1(S, gamma, text[i - 1])
    crit_pos, shift = i - gamma.depth + 1, S.m - gamma.depth
    i += shift
    if i > n:
      return
    gamma = _next2(S, text, crit_pos - 1, i - 1)
