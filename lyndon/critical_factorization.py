import operator

from common import prefix
from lyndon import maximum_suffix

def local_period_naive(text_left, text_right):
  for i in range(1, len(text_right) + 1):
    w = text_right[:i]
    if text_left.endswith(w) or w.endswith(text_left):
      return w
  for i in range(1, len(text_left) + 1):
    w = text_right + text_left[-i:]
    if text_left.endswith(w) or w.endswith(text_left):
      return w
  return None

def naive_all(text, n):
  p = prefix.period(text, n)
  out = []
  for i in range(1, n + 2):
    w = local_period_naive(text[1:i], text[i:])
    if len(w) == p:
      out.append((i, prefix.period(text[0] + text[i:], n + 1 - i)))
  return out

def constant_space(text, n):
  index_lt, p_lt = maximum_suffix.constant_space(text, n)
  index_gt, p_gt = maximum_suffix.constant_space(
      text, n, less = operator.__gt__)
  return (index_lt, p_lt) if index_lt >= index_gt else (index_gt, p_gt)
