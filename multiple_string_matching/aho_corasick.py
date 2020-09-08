import queue

from common import dawg

class AhoCorasick:
  def __init__(self, W):
    self.root = dawg.AutomatonNode()
    self._create_automaton(W)

  def _create_trie(self, W):
    for word in W:
      current_node = self.root
      for c in word:
        new_node = dawg.AutomatonNode(current_node.depth + 1)
        if c not in current_node.children:
            current_node.add_child(new_node, c)
        current_node = current_node.children[c]
      current_node.output.append(word)

  def _create_automaton(self, W):
    self._create_trie(W)
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
