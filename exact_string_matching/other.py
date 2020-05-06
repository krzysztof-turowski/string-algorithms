import math

from exact_string_matching import forward
from lyndon import critical_factorization
from string_indexing import suffix_tree

def fast_on_average(text, word, n, m):
  ST, _ = suffix_tree.mccreight(word, m)
  i, r = m, min(2 * math.ceil(math.log(m, 2)), m - 1)
  while i <= n:
    if ST.find_node(text[(i - r):(i + 1)], r + 1) is not None:
      subtext = text[0] + text[(i - m + 1):(i + m - r)]
      subn = min(i + m - r, n + 1) - (i - m + 1)
      yield from [v + i - m
                  for v in forward.knuth_morris_pratt(subtext, word, subn, m)]
    i = i + m - r

def two_way(text, word, n, m):
  index, p, use_memory = *critical_factorization.constant_space(word, m), True
  if index - 1 > m / 2 or not word[index:index + p].endswith(word[1:index]):
    p, use_memory = max(len(word[1:index]), len(word[index:])) + 1, False
  i, memory = 1, 0
  while i <= n - m + 1:
    j = max(index - 1, memory)
    while j < m and text[i + j] == word[j + 1]:
      j = j + 1
    if j < m:
      i, memory = i + j + 2 - index, 0
      continue
    j = max(index - 1, memory)
    while j > memory and text[i + j - 1] == word[j]:
      j = j - 1
    if j == memory:
      yield i
    i, memory = i + p, m - p if use_memory else 0
