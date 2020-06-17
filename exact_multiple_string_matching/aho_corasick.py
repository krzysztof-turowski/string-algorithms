from queue import Queue


def create_aho_corasick_automaton(keywords, alphabet='ab'):
  return AhoCorasickAutomaton(keywords, alphabet)


def find_occurrences(text, n, ac_automaton):
  return ac_automaton.find_occurrences(text, n)


# pylint: disable=too-few-public-methods
class AhoCorasickAutomaton:
  def __init__(self, keywords, alphabet):
    self._root = AhoCorasickAutomaton.Node()
    self._construct_goto(keywords, alphabet)
    self._construct_fail(alphabet)
    self._construct_nxt(alphabet)

  def _construct_goto(self, keywords, alphabet):
    for k, k_len in keywords:
      self._enter(k, k_len)

    for a in alphabet:
      if self._root.goto(a) is None:
        self._root.update_goto(a, self._root)

  def _enter(self, keyword, keyword_len):
    current_state = self._root
    j = 1

    while j < keyword_len and current_state.goto(keyword[j]) is not None:
      current_state = current_state.goto(keyword[j])
      j += 1

    for a in keyword[j:keyword_len + 1]:
      next_state = AhoCorasickAutomaton.Node()
      current_state.update_goto(a, next_state)
      current_state = next_state

    current_state.append_outputs([keyword_len])

  def _construct_fail(self, alphabet):
    q = Queue()
    for s in [self._root.goto(a) for a in alphabet]:
      if s != self._root:
        q.put(s)
        s.update_fail(self._root)

    while not q.empty():
      current = q.get()
      for a, child in [(a, current.goto(a)) for a in alphabet]:
        if child is not None:
          q.put(child)

          fallback = current.fail()
          while fallback.goto(a) is None:
            fallback = fallback.fail()

          child_fallback = fallback.goto(a)
          child.update_fail(child_fallback)
          child.append_outputs(child_fallback.output())

  def _construct_nxt(self, alphabet):
    q = Queue()
    for a in alphabet:
      a_child = self._root.goto(a)
      self._root.update_nxt(a, a_child)
      if a_child != self._root:
        q.put(a_child)
    self._root.use_only_nxt()

    while not q.empty():
      current = q.get()
      for a, child in [(a, current.goto(a)) for a in alphabet]:
        if child is not None:
          q.put(child)
          current.update_nxt(a, child)
        else:
          fallback = current.fail()
          current.update_nxt(a, fallback.nxt(a))
      current.use_only_nxt()

  def find_occurrences(self, text, n):
    state = self._root
    for i in range(1, n + 1):
      state = state.nxt(text[i])
      for keyword_len in state.output():
        yield i - keyword_len + 1, i + 1

  class Node:
    def __init__(self):
      self._goto, self._fail, self._output, self._nxt = {}, None, [], {}

    def goto(self, a):
      return self._goto.get(a, None)

    def update_goto(self, a, target_node):
      self._goto[a] = target_node

    def output(self):
      return self._output

    def append_outputs(self, outputs):
      self._output += outputs

    def fail(self):
      return self._fail

    def update_fail(self, target_node):
      self._fail = target_node

    def nxt(self, a):
      return self._nxt[a]

    def update_nxt(self, a, target_node):
      self._nxt[a] = target_node

    def use_only_nxt(self):
      del self._goto
      del self._fail
