from common import dawg
from multiple_string_matching import aho_corasick

class FastPracticalMultipleStringMatching:
  def __init__(self, W):
    self.acm = aho_corasick.AhoCorasick(W)
    self.dawg = dawg.DAWG([w[::-1] for w in W])
    self.m = min(len(w) for w in W)

def build(W):
  return FastPracticalMultipleStringMatching([w[1:] for w in W])

def search(t, n, automaton):
  i, gamma = 1, automaton.acm.root
  while True:
    while gamma.depth >= automaton.m / 2:
      if gamma.output:
        for match in gamma.output:
          yield (match, i - len(match))
      i += 1
      if i > n + 1:
        return
      gamma = automaton.acm.step(gamma, t[i - 1])
    crit_pos, shift = i - gamma.depth + 1, automaton.m - gamma.depth
    i += shift
    if i > n + 1:
      return
    gamma = automaton.acm.traverse(
        automaton.dawg.traverse(t, crit_pos - 1, i - 1))
