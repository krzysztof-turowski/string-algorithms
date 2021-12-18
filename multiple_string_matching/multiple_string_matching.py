import collections
import math
import queue

from common import trie, dawg

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

def aho_corasick_build(W):
  return AhoCorasick([w[1:] for w in W])

def aho_corasick_search(t, n, automaton):
  i, gamma = 1, automaton.root
  while True:
    yield from ((match, i - len(match)) for match in gamma.output)
    i += 1
    if i > n + 1:
      return
    gamma = automaton.step(gamma, t[i - 1])

class CommentzWalterNode(AhoCorasickNode):
  def __init__(self, label, depth = 0):
    super().__init__(label, depth)
    self.shift1, self.shift2 = math.inf, math.inf

class CommentzWalter(AhoCorasick):
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
    Q, L = collections.deque(), []
    Q.extend(self.root.children.values())
    while Q:
      node = Q.popleft()
      L.append(node)
      Q.extend(node.children[key] for key in node.children)
    for node in L[::-1]:
      difference = node.depth - node.fail.depth
      node.fail.shift1 = min(node.fail.shift1, difference)
      if node.output:
        node.fail.shift2 = min(node.fail.shift2, difference)
      node.fail.shift2 = min(node.fail.shift2, node.shift2 + difference)
    self.root.shift1, self.root.shift2 = 1, self.min_depth
    for node in L:
      node.shift1 = min(node.shift1, self.min_depth)
      node.shift2 = min(node.shift2, node.parent.shift2)

  def shift(self, node, j):
    if node.parent is None:
      shift = node.shift1
    else:
      min_depth = self.min_letter_depth.get(node.label, self.min_depth + 1)
      shift = max(min_depth - j, node.shift1)
    return min(shift, node.shift2)

def commentz_walter_build(W):
  return CommentzWalter([w[:0:-1] for w in W])

def commentz_walter_search(t, n, automaton):
  i = automaton.min_depth - 1
  while i < n:
    v, j, c = automaton.root, 0, t[i + 1]
    while c in v.children and i >= j:
      v, j = v.children[c], j + 1
      yield from ((w, i - j + 2) for w in v.output)
      c = t[i - j + 1]
    i += automaton.shift(v, min(i, j))

# pylint: disable=too-few-public-methods
class FastPracticalMultipleStringMatching:
  def __init__(self, W):
    self.acm = AhoCorasick(W)
    self.dawg = dawg.DAWG([w[::-1] for w in W])
    self.min_depth = min(len(w) for w in W)

def fast_practical_multi_string_matching_build(W):
  return FastPracticalMultipleStringMatching([w[1:] for w in W])

def fast_practical_multi_string_matching_search(t, n, automaton):
  i, gamma = 1, automaton.acm.root
  while True:
    while gamma.depth >= automaton.min_depth // 2:
      if gamma.output:
        for match in gamma.output:
          yield (match, i - len(match))
      i += 1
      if i > n + 1:
        return
      gamma = automaton.acm.step(gamma, t[i - 1])
    crit_pos, shift = i - gamma.depth + 1, automaton.min_depth - gamma.depth
    i += shift
    if i > n + 1:
      return
    gamma = automaton.acm.traverse(
        automaton.dawg.traverse(t, crit_pos - 1, i - 1))
