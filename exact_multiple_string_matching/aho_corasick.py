from queue import Queue


def create_aho_corasick_automaton(keywords, alphabet='ab'):
  return AhoCorasickAutomaton(keywords, alphabet)


def find_occurrences(text, n, ac_automaton):
  return ac_automaton.find_occurrences(text, n)


class AhoCorasickAutomaton:
  def __init__(self, keywords, alphabet):
    self._root = AhoCorasickAutomaton.Node()
    self._construct_goto(keywords, alphabet)
    self._construct_fail(alphabet)
    self._construct_next(alphabet)

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

    current_state.append_outputs([(keyword, keyword_len)])

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

  def _construct_next(self, alphabet):
    q = Queue()
    for a in alphabet:
      a_child = self._root.goto(a)
      self._root.update_next(a, a_child)
      if a_child != self._root:
        q.put(a_child)
    self._root.use_only_next()

    while not q.empty():
      current = q.get()
      for a, child in [(a, current.goto(a)) for a in alphabet]:
        if child is not None:
          q.put(child)
          current.update_next(a, child)
        else:
          fallback = current.fail()
          current.update_next(a, fallback.next(a))
      current.use_only_next()

  def find_occurrences(self, text, n):
    state = self._root
    for i in range(1, n + 1):
      state = state.next(text[i])
      for keyword, keyword_len in state.output():
        yield i - keyword_len + 1, keyword

  class Node:
    def __init__(self):
      self._goto, self._fail, self._output, self._next = {}, None, [], {}

    def goto(self, a):
      return self._goto.get(a, None)

    def update_goto(self, a, target_node):
      self._goto[a] = target_node

    def output(self):
      return self._output

    def append_outputs(self, words):
      self._output += words

    def fail(self):
      return self._fail

    def update_fail(self, target_node):
      self._fail = target_node

    def next(self, a):
      return self._next[a]

    def update_next(self, a, target_node):
      self._next[a] = target_node

    def use_only_next(self):
      del self._goto
      del self._fail


if __name__ == '__main__':
  ac = create_aho_corasick_automaton([('#he', 2), ('#she', 3),
                                      ('#his', 3), ('#hers', 4)],
                                     'hesru')
  for i, p in ac.find_occurrences('#ushers', 6, ):
    print(i, p)
