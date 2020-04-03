import math

from exact_string_matching import forward
from string_indexing import suffix_tree

def fast_on_average(text, word, n, m):
  ST, _ = suffix_tree.mccreight(word, m)
  i, r = m, min(2 * math.ceil(math.log(m, 2)), m - 1)
  while i <= n:
    if ST.find_node(text[(i - r):(i + 1)], r + 1) is not None:
      subtext = text[0] + text[(i - m + 1):(i + m - r)]
      subn = min(i + m - r, n + 1) - (i - m + 1)
      yield from [v + i - m for v in forward.knuth_morris_pratt(subtext, word, subn, m)]
    i = i + m - r
