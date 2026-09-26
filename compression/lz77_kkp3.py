import collections
from dataclasses import dataclass
import math

from common import numeric
from string_indexing import suffix_array

Parameters = collections.namedtuple(
    'Parameters', ['alpha', 'n', 'max_length', 'Lp', 'Ll', 'Lc'])

def make_parameters(alpha, n, max_length):
  if alpha < 2:
    raise ValueError('alpha >= 2 expected')
  if n < 0:
    raise ValueError('n >= 0 expected')
  Lp = math.ceil(math.log(max(n, 1), alpha))
  Ll = math.ceil(math.log(max_length + 1, alpha))
  return Parameters(alpha, n, max_length, Lp, Ll, 1 + Lp + Ll)

# Stats
@dataclass
class Stats:
  source_symbols: int = 0
  words: int = 0

def compression_ratio(stats, parameters):
  if stats.source_symbols == 0:
    return 0.0
  return stats.words * parameters.Lc / stats.source_symbols


# Factorization
NextPrevSmallerValue = collections.namedtuple(
  'NextPrevSmallerValue', ['next', 'prev'])

def _compute_kkp_smaller_values(sa, n):
  out = NextPrevSmallerValue([0] * (n + 2), [0] * (n + 2))
  top = 0
  for i in range(1, n + 2):
    while sa[top] > sa[i]:
      out.next[sa[top]], out.prev[sa[top]] = sa[i], sa[top - 1]
      top -= 1
    top += 1
    sa[top] = sa[i]
  return out

def _longest_common_prefix(w, n, i, j):
  if j == 0:
    return 0
  length = 0
  while (i + length <= n and j + length <= n
         and w[i + length] == w[j + length]):
    length += 1
  return length

Factor = collections.namedtuple(
  'Factor', ['position', 'length', 'literal'])

def karkkainen_kempa_puglisi_factorization(w, n, SA = None):
  SA = SA or suffix_array.induced_sorting(w, n)
  return _compute_kkp_smaller_values(
      [0] + [SA[j] for j in range(1, n + 1)] + [0], n)

def factorize(w, n, smaller_values = None):
  """
  Greedy factorization into Lc
  """
  if smaller_values is None:
    smaller_values = karkkainen_kempa_puglisi_factorization(w, n)
  factors, i = [], 1
  while i <= n:
    prev, following = smaller_values.prev[i], smaller_values.next[i]
    prev_length = _longest_common_prefix(w, n, i, prev)
    next_length = _longest_common_prefix(w, n, i, following)
    if prev_length > next_length:
      position, length = prev, prev_length
    else:
      position, length = following, next_length
    if i + length > n:
      length = n - i
    factors.append(Factor(position if length > 0 else 1,
                           length, w[i + length]))
    i += length + 1
  return factors

# Encoder
class Encoder:
  def __init__(self, w, n, A):
    self.factors = factorize(w, n) if n > 0 else []
    self.rank = {c: i for i, c in enumerate(A)}
    self.next, self.stats = 0, Stats()

    # compute Ll with actual max_length
    max_length = max((f.length for f in self.factors), default = 0)
    self.parameters = make_parameters(len(A), n, max_length)
    self.stats.source_symbols = n

  def has_more(self):
    return self.next < len(self.factors)

  def encode_next(self):
    factor = self.factors[self.next]
    self.next += 1
    self.stats.words += 1
    return (numeric.to_radix(
              factor.position - 1, self.parameters.alpha, self.parameters.Lp)
            + numeric.to_radix(
              factor.length, self.parameters.alpha, self.parameters.Ll)
            + [self.rank[factor.literal]])

  def encode_all(self):
    stream = []
    while self.has_more():
      stream += self.encode_next()
    return stream

# Decoder
class Decoder:
  def __init__(self, parameters):
    self.parameters, self.out = parameters, [-1]

  def decode_next(self, C):
    if len(C) != self.parameters.Lc:
      raise ValueError('codeword of length Lc expected')
    position = numeric.from_radix(
        C[:self.parameters.Lp], self.parameters.alpha) + 1
    length = numeric.from_radix(
        C[self.parameters.Lp:self.parameters.Lp + self.parameters.Ll],
        self.parameters.alpha)
    if not 1 <= position <= len(self.out) - 1 and length > 0:
      raise ValueError('pointer out of range')
    if not 0 <= length <= self.parameters.max_length:
      raise ValueError('length out of range')

    for k in range(length):
      self.out.append(self.out[position + k])
    self.out.append(C[-1])
    return self.out[-(length + 1):]

  def decode_all(self, stream, source_length = 0):
    if len(stream) % self.parameters.Lc != 0:
      raise ValueError('stream length is not a multiple of Lc')
    for i in range(0, len(stream), self.parameters.Lc):
      self.decode_next(stream[i:i + self.parameters.Lc])
    out = self.out[1:]
    return out[:source_length] if source_length else out

def compress(source, n, A = None):
  A = sorted(set(source[1:n + 1])) if A is None else sorted(A)
  encoder = Encoder(source[:n + 1], n, A)
  return encoder.encode_all(), encoder.parameters, A, encoder.stats

def decompress(stream, n, parameters, A):
  return '#' + ''.join(A[s] for s in Decoder(parameters).decode_all(stream, n))
