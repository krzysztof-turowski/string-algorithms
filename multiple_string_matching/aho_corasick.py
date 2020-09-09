import queue

from common import trie

class AhoCorasickNode(trie.TrieNode):
  def __init__(self, w, depth = 0):
    super().__init__(w)
    self.fail, self.output, self.depth = None, [], depth

class AhoCorasick:
  def __init__(self, W, reverse_word = False, add_to_output = True):
    self.root = self.create_node('')
    self.create_trie(W, reverse_word)
    self.create_automaton(add_to_output)

  @staticmethod
  def create_node(label, depth = 0):
    return AhoCorasickNode(label, depth)

  def create_trie(self, W, reverse_word):
    for word in W:
      current_node = self.root
      for c in word:
        if c not in current_node.children:
          new_node = self.create_node(c, current_node.depth + 1)
          current_node.add_child(new_node)
        current_node = current_node.children[c]
      current_node.output.append(word[::-1] if reverse_word else word)

  def create_automaton(self, add_to_output):
    Q = queue.Queue()
    for node in self.root.children.values():
      Q.put(node)
      node.fail = self.root
    while not Q.empty():
      current_node = Q.get()
      for label, next_node in current_node.children.items():
        Q.put(next_node)
        fail_node = current_node.fail
        while fail_node is not None and label not in fail_node.children:
          fail_node = fail_node.fail
        next_node.fail = fail_node.children[label] if fail_node else self.root
        if add_to_output:
          next_node.output += next_node.fail.output

  def step(self, node, label):
    while label not in node.children and node is not self.root:
      node = node.fail
    return node.children[label] if label in node.children else self.root

  def traverse(self, t):
    node = self.root
    for c in t:
      node = self.step(node, c)
    return node

def build(W):
  return AhoCorasick([w[1:] for w in W])

def search(t, n, automaton):
  i, gamma = 1, automaton.root
  while True:
    yield from ((match, i - len(match)) for match in gamma.output)
    i += 1
    if i > n + 1:
      return
    gamma = automaton.step(gamma, t[i - 1])
