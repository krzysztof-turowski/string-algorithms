import math

from exact_string_matching import forward
from string_indexing import suffix_tree

def fast_on_average(t, w, n, m):
  ST, _ = suffix_tree.mccreight(w, m)
  i, r = m, min(2 * math.ceil(math.log(m, 2)), m - 1)
  while i <= n:
    if ST.contains(t[(i - r):(i + 1)]):
      subt = t[0] + t[(i - m + 1):min(i + m - r, n + 1)]
      subn = min(i + m - r, n + 1) - (i - m + 1)
      yield from [v + i - m for v in forward.knuth_morris_pratt(subt, w, subn, m)]
    i = i + m - r
