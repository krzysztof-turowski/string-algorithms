import math
import random
import scipy.signal

from exact_string_matching import forward
from lyndon import critical_factorization
from string_indexing import suffix_tree

def karp_rabin(text, word, n, m):
  MOD = 257
  A = random.randint(2, MOD - 1)
  Am = pow(A, m, MOD)
  def generate(t):
    return sum(ord(c) * pow(A, i, MOD) for i, c in enumerate(t[::-1])) % MOD
  text += '$'
  hash_text, hash_word = generate(text[1:m + 1]), generate(word[1:])
  for i in range(1, n - m + 2):
    if hash_text == hash_word and text[i:i + m] == word[1:]:
      yield i
    hash_text = (A * hash_text + ord(text[i + m]) - Am * ord(text[i])) % MOD

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

def fft(text, word, n, m):
  if n < m:
    return
  A = set(list(text[1:] + word[1:]))
  letter_mapping = {c: i for i, c in enumerate(A, start = 1)}
  text = [letter_mapping.get(c) for c in text[1:]]
  word = [letter_mapping.get(c) for c in word[:0:-1]]

  convolutions = scipy.signal.convolve(
      text, word, mode = 'valid', method = 'fft')
  p, t = sum(c * c for c in word), sum(c * c for c in text[:m])
  text += [0]
  for index, convolution in enumerate(convolutions):
    if t + p - 2 * convolution == 0:
      yield index + 1
    t = t + text[index + m] ** 2 - text[index] ** 2
