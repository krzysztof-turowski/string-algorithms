
from common import prefix

# computes ov(w_1, w_2)
def _overlap(w_1, w_2):
  if w_1 != w_2:
    w = w_2 + w_1
  else:
    w = w_1
  return prefix.prefix_suffix(w, len(w) - 1)[len(w) - 1]

# achieves 4-approximation
def greedy(words):
  S = set(words)
  while len(S) > 1:
    best_ov = -1
    chosen_pair = ('','')
    for w_1 in S:
      for w_2 in S:
        if w_1 == w_2:
          continue
        ov = _overlap(w_1, w_2)
        if ov > best_ov:
          best_ov = ov
          chosen_pair = (w_1, w_2)
    w_1, w_2 = chosen_pair
    S.remove(w_1)
    S.remove(w_2)
    S.add(w_1 + w_2[best_ov + 1:])
  return ''.join(S)

# first phase of mgreedy, computes the set T
def _mgreedy_first_phase(words):
  S = set(words)
  T = set()
  while S:
    best_ov = -1
    chosen_pair = ('','')
    for w_1 in S:
      for w_2 in S:
        ov = _overlap(w_1, w_2)
        if ov > best_ov:
          best_ov = ov
          chosen_pair = (w_1, w_2)
    w_1, w_2 = chosen_pair
    S.remove(w_1)
    if w_1 != w_2:
      S.remove(w_2)
      S.add(w_1 + w_2[best_ov + 1:])
    else:
      T.add(w_1)
  return T

# achieves 3-approximation
def tgreedy(words):
  return greedy(_mgreedy_first_phase(words))
