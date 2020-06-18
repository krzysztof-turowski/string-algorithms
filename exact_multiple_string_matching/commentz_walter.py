from dataclasses import dataclass
from collections import deque

@dataclass
class Node():
  def __init__(self, char, depth, parent):
    self.char = char
    self.depth = depth
    self.word = None
    self.parent = parent
    self.ac_suffix = None
    self.ac_output = None
    self.children = {}

@dataclass
class CommentzWalterNode(Node):
  def __init__(self, char, depth, parent):
    Node.__init__(self, char, depth, parent)
    self.min_diff_s1 = -1
    self.min_diff_s2 = -1
    self.cw_suffix = None
    self.cw_output = None
    self.shift1 = None
    self.shift2 = None

# pylint: disable=no-self-use
class Trie():
  def create_node(self, char, depth, parent):
    return Node(char, depth, parent)

  def __init__(self):
    self.size = 0
    self.root = self.create_node(None, 0, None)

  def add_word(self, word):
    curr_node = self.root
    curr_depth = 1
    for char in word:
      next_node = curr_node.children.get(char)
      if not next_node:
        next_node = self.create_node(char, curr_depth, curr_node)
        curr_node.children[char] = next_node

      curr_node = next_node
      curr_depth += 1

    if curr_node.word is not None:
      return

    curr_node.word = word
    self.size += 1

class CommentzWalterAutomaton(Trie):
  def create_node(self, char, depth, parent):
    return CommentzWalterNode(char, depth, parent)

  def __init__(self):
    Trie.__init__(self)
    self.min_depth = None
    self.char_arr = {}

  def add_word(self, word):
    word = word[::-1]
    super().add_word(word)
    pos = 1

    for char in word:
      min_char_depth = self.char_arr.get(char)
      if (min_char_depth is None) or (min_char_depth > pos):
        self.char_arr[char] = pos
      pos += 1

    if self.min_depth is None or len(word) < self.min_depth:
      self.min_depth = len(word)

  def init_shift_values(self):
    bfs_queue = deque()
    self.root.shift1 = 1
    self.root.shift2 = self.min_depth

    for key in self.root.children:
      bfs_queue.append(self.root.children[key])

    while bfs_queue:
      curr_node = bfs_queue.popleft()

      if curr_node.cw_suffix is None:
        curr_node.shift1 = self.min_depth
      else:
        curr_node.shift1 = curr_node.min_diff_s1

      if curr_node.cw_output is None:
        curr_node.shift2 = curr_node.parent.shift2
      else:
        curr_node.shift2 = curr_node.min_diff_s2

      for key in curr_node.children:
        bfs_queue.append(curr_node.children[key])

  def create_failure_links(self):
    bfs_queue = deque()

    for key in self.root.children:
      child = self.root.children[key]
      child.ac_suffix = self.root

      for key2 in child.children:
        bfs_queue.append(child.children[key2])

    while bfs_queue:
      curr_node = bfs_queue.popleft()
      for key in curr_node.children:
        bfs_queue.append(curr_node.children[key])

      search = curr_node.parent.ac_suffix

      while (not search.char is None) and \
      (not search.children.get(curr_node.char) is not None):
        search = search.ac_suffix

      if search.children.get(curr_node.char) is not None:
        ac_suffix_node = search.children[curr_node.char]
      else:
        ac_suffix_node = search

      curr_node.ac_suffix = ac_suffix_node
      suffix_is_word = curr_node.ac_suffix.word is not None
      curr_node.ac_output = curr_node.ac_suffix \
      if suffix_is_word else curr_node.ac_suffix.ac_output
      if curr_node.ac_output is not None:
        pass

      difference = curr_node.depth - ac_suffix_node.depth

      if ac_suffix_node.min_diff_s1 == -1 or \
      ac_suffix_node.min_diff_s1 > difference:
        ac_suffix_node.min_diff_s1 = difference
        ac_suffix_node.cw_suffix = curr_node

      if curr_node.word is not None:
        if ac_suffix_node.min_diff_s2 == -1 or \
        ac_suffix_node.min_diff_s2 > difference:
          ac_suffix_node.min_diff_s2 = difference
          ac_suffix_node.cw_output = curr_node

    self.init_shift_values()

  def shift_func(self, node, j):
    max_min_diff_s1_char = 0
    if node.char is None:
      max_min_diff_s1_char = node.shift1
    else:
      min_depth = self.char_arr.get(node.char)
      if min_depth is None:
        min_depth = self.min_depth + 1
      max_min_diff_s1_char = max(min_depth - j - 1, node.shift1)
    return min(max_min_diff_s1_char, node.shift2)

  def report_all_matches(self, text, n):
    i = self.min_depth - 1

    while i < n:
      v, j = self.root, 0
      c_find = text[i]

      while v.children.get(c_find) is not None and i >= j:
        v = v.children[c_find]
        j += 1
        if v.word is not None:
          yield (v.word[::-1], i - j + 1)
        c_find = text[i - j]

      j = min(i, j)
      i += self.shift_func(v, j)

def commentz_walter_build(W):
  cw_auto = CommentzWalterAutomaton()
  for word in W:
    cw_auto.add_word(word)
  cw_auto.create_failure_links()
  return cw_auto

def commentz_walter_search(text, n, S):
  return S.report_all_matches(text, n)
