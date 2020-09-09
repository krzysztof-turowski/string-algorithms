import collections
import math

from multiple_string_matching import aho_corasick

class CommentzWalterNode(aho_corasick.AhoCorasickNode):
  def __init__(self, label, depth = 0):
    super().__init__(label, depth)
    self.shift1, self.shift2 = math.inf, math.inf

class CommentzWalter(aho_corasick.AhoCorasick):
  def __init__(self, W):
    super().__init__(W, reverse_word = True, add_to_output = False)
    self.min_depth, self.min_letter_depth = math.inf, {}
    self.compute_depth(W)
    self.compute_shift_values()

  @staticmethod
  def create_node(label, depth = 0):
    return CommentzWalterNode(label, depth)

  def compute_depth(self, W):
    for word in W:
      for i, c in enumerate(word):
        if c not in self.min_letter_depth or self.min_letter_depth[c] > i:
          self.min_letter_depth[c] = i
      self.min_depth = min(self.min_depth, len(word))

  def compute_shift_values(self):
    self.root.shift1, self.root.shift2 = 1, self.min_depth
    Q = collections.deque()
    Q.extend(self.root.children[key] for key in self.root.children)
    while Q:
      node = Q.popleft()
      difference = node.depth - node.fail.depth
      if node.fail.shift1 > difference:
        node.fail.shift1 = difference
      if node.output and node.fail.shift2 > difference:
        node.fail.shift2 = difference
      Q.extend(node.children[key] for key in node.children)

    Q = collections.deque()
    Q.extend(self.root.children[key] for key in self.root.children)
    while Q:
      node = Q.popleft()
      node.shift1 = min(node.shift1, self.min_depth)
      node.shift2 = min(node.shift2, node.parent.shift2)
      Q.extend(node.children[key] for key in node.children)

  def shift(self, node, j):
    if node.parent is None:
      shift = node.shift1
    else:
      min_depth = self.min_letter_depth.get(node.label, self.min_depth + 1)
      shift = max(min_depth - j, node.shift1)
    return min(shift, node.shift2)

def build(W):
  return CommentzWalter([w[:0:-1] for w in W])

def search(t, n, automaton):
  i = automaton.min_depth - 1
  while i < n:
    v, j, c = automaton.root, 0, t[i + 1]
    while c in v.children and i >= j:
      v, j = v.children[c], j + 1
      yield from ((w, i - j + 2) for w in v.output)
      c = t[i - j + 1]
    i += automaton.shift(v, min(i, j))
