import math
import random
import scipy.signal

from exact_string_matching import forward
from lyndon import critical_factorization
from string_indexing import suffix_tree

def karp_rabin(t, w, n, m):
  MOD = 257
  A = random.randint(2, MOD - 1)
  Am = pow(A, m, MOD)
  def generate(t):
    return sum(ord(c) * pow(A, i, MOD) for i, c in enumerate(t[::-1])) % MOD
  t += '$'
  hash_t, hash_w = generate(t[1:m + 1]), generate(w[1:])
  for i in range(1, n - m + 2):
    if hash_t == hash_w and t[i:i + m] == w[1:]:
      yield i
    hash_t = (A * hash_t + ord(t[i + m]) - Am * ord(t[i])) % MOD

def fast_on_average(t, w, n, m):
  ST, _ = suffix_tree.mccreight(w, m)
  i, r = m, min(2 * math.ceil(math.log(m, 2)), m - 1)
  while i <= n:
    if ST.find_node(t[(i - r):(i + 1)], r + 1) is not None:
      t_sub = t[0] + t[(i - m + 1):(i + m - r)]
      n_sub = min(i + m - r, n + 1) - (i - m + 1)
      yield from [
        v + i - m for v in forward.knuth_morris_pratt(t_sub, w, n_sub, m)]
    i = i + m - r

def two_way(t, w, n, m):
  index, p, use_memory = *critical_factorization.constant_space(w, m), True
  if index - 1 > m / 2 or not w[index:index + p].endswith(w[1:index]):
    p, use_memory = max(len(w[1:index]), len(w[index:])) + 1, False
  i, memory = 1, 0
  while i <= n - m + 1:
    j = max(index - 1, memory)
    while j < m and t[i + j] == w[j + 1]:
      j = j + 1
    if j < m:
      i, memory = i + j + 2 - index, 0
      continue
    j = max(index - 1, memory)
    while j > memory and t[i + j - 1] == w[j]:
      j = j - 1
    if j == memory:
      yield i
    i, memory = i + p, m - p if use_memory else 0

def fft(t, w, n, m):
  if n < m:
    return
  A = set(list(t[1:] + w[1:]))
  letter_mapping = {c: i for i, c in enumerate(A, start = 1)}
  t = [letter_mapping.get(c) for c in t[1:]]
  w = [letter_mapping.get(c) for c in w[:0:-1]]
  convolutions = scipy.signal.convolve(t, w, mode = 'valid', method = 'fft')
  p, q = sum(c * c for c in w), sum(c * c for c in t[:m])
  t += [0]
  for index, convolution in enumerate(convolutions):
    if q + p - 2 * convolution == 0:
      yield index + 1
    q += t[index + m] ** 2 - t[index] ** 2
