from itertools import product
from itertools import permutations

from common import prefix

# computes ov(w_1, w_2)
def overlap(w_1, w_2):
  w = w_1 if w_1 == w_2 else w_2 + w_1
  return prefix.prefix_suffix(w, len(w) - 1)[len(w) - 1]

# achieves 4-approximation
def greedy(words):
  S = set(words)
  while len(S) > 1:
    best_ov, chosen_pair = -1, None
    for w_1, w_2 in permutations(S, 2):
      ov = overlap(w_1, w_2)
      if ov > best_ov:
        best_ov, chosen_pair = ov, (w_1, w_2)
    w_1, w_2 = chosen_pair
    S.remove(w_1)
    S.remove(w_2)
    S.add(w_1 + w_2[best_ov + 1:])
  return ''.join(S)

# first phase of mgreedy, computes the set T
def _mgreedy_first_phase(words):
  S, T = set(words), set()
  while S:
    best_ov, chosen_pair = -1, None
    for w_1, w_2 in product(S, repeat=2):
      ov = overlap(w_1, w_2)
      if ov > best_ov:
        best_ov, chosen_pair = ov, (w_1, w_2)
    w_1, w_2 = chosen_pair
    S.remove(w_1)
    if w_1 != w_2:
      S.remove(w_2)
      S.add(w_1 + w_2[best_ov + 1:])
    else:
      T.add(w_1)
  return T

# achieves 4-approximation
def mgreedy(words):
  return next(iter(words), [''])[0] + \
         ''.join(w[1:] for w in _mgreedy_first_phase(words))

# achieves 3-approximation
def tgreedy(words):
  return greedy(_mgreedy_first_phase(words))
