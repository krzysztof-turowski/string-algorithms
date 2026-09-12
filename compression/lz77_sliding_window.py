import collections
import math

from common import numeric

Parameters = collections.namedtuple(
    'Parameters', ['alpha', 'n', 'Ls', 'Lp', 'Ll', 'Lc', 'window_size'])

def make_parameters(alpha, n, Ls):
  if alpha < 2:
    raise ValueError('alpha >= 2 expected')
  if Ls < 1:
    raise ValueError('Ls >= 1 expected')
  if n - Ls < Ls:
    raise ValueError('n - Ls >= Ls expected')
  Lp = math.ceil(math.log(n - Ls, alpha))
  Ll = math.ceil(math.log(Ls, alpha))
  return Parameters(alpha, n, Ls, Lp, Ll, 1 + Lp + Ll, n - Ls)

#----------------------------------------------------
# Stats
# @dataclass
class Stats:
  def __init__(self):
    self.source_symbols, self.words = 0, 0

def compression_ratio(stats, parameters):
  if stats.source_symbols == 0:
    return 0.0
  return stats.words * parameters.Lc / stats.source_symbols
#----------------------------------------------------


#----------------------------------------------------
# Ring buffer of size exactly n for faster shifting
class Ring:
  """
  Cyclic buffer of a fixed size, indexed relative to its head
  """
  def __init__(self, size):
    self.data, self.size, self.head = [0] * size, size, 0

  def _fast_module(self, x):
    return x if x < self.size else x - self.size

  def at(self, k):
    return self.data[self._fast_module(self.head + k)]

  def set(self, k, s):
    self.data[self._fast_module(self.head + k)] = s

  def shift_in(self, s):
    self.data[self.head] = s
    self.head = self._fast_module(self.head + 1)

  def slice(self, begin, count):
    return [self.at(begin + k) for k in range(count)]
#----------------------------------------------------



# Encoder
def _reproducible_extension(ring, j, m):
  """
  Longest prefix of B(j + 1 .. m) that occurs in B(1 .. m)
  and starts in B(1 .. j)
  """
  max_length, best_position, best_length = m - j, 1, 0
  for i in range(1, j + 1):
    length = 0
    while (length < max_length
           and ring.at(i - 1 + length) == ring.at(j + length)):
      length += 1
    if length >= best_length:
      best_position, best_length = i, length
  return best_position, best_length

class Encoder:
  def __init__(self, parameters, source):
    self.parameters, self.source = parameters, list(source)
    self.buffer = Ring(parameters.n)
    self.position, self.encoded, self.stats = 0, 0, Stats()
    for i in range(parameters.Ls):
      self.buffer.set(parameters.window_size + i, self._next_symbol())

  def _next_symbol(self):
    """
    Symbols past the end of the source are padded with 0
    """
    if self.position >= len(self.source):
      return 0
    self.position += 1
    return self.source[self.position - 1]

  def has_more(self):
    return self.encoded < len(self.source)

  def encode_next(self):
    j = self.parameters.window_size
    position, length = _reproducible_extension(
      self.buffer, j, self.parameters.n - 1)
    parsed_length = length + 1

    C = (numeric.to_radix(
            position - 1, self.parameters.alpha, self.parameters.Lp)
         + numeric.to_radix(
            length, self.parameters.alpha, self.parameters.Ll)
         + [self.buffer.at(j + length)])

    for _ in range(parsed_length):
      self.buffer.shift_in(self._next_symbol())

    self.encoded += parsed_length
    self.stats.words += 1

    # last source block fallback
    self.stats.source_symbols = min(self.encoded, len(self.source))
    return C

  def encode_all(self):
    stream = []
    while self.has_more():
      stream += self.encode_next()
    return stream
#---------------------------------------------------


#--------------------------------------------------
#Decoder
class Decoder:
  def __init__(self, parameters):
    self.parameters, self.buffer = parameters, Ring(parameters.window_size)

  def _cell(self, p):
    return self.buffer.at(p - 1)

  def decode_next(self, C):
    if len(C) != self.parameters.Lc:
      raise ValueError('codeword of length Lc expected')
    position = numeric.from_radix(
      C[:self.parameters.Lp], self.parameters.alpha) + 1
    length = numeric.from_radix(
      C[self.parameters.Lp:self.parameters.Lp + self.parameters.Ll],
      self.parameters.alpha) + 1
    if not 1 <= position <= self.parameters.window_size:
      raise ValueError('pointer out of range')
    if not 1 <= length <= self.parameters.Ls:
      raise ValueError('length out of range')

    for _ in range(length - 1):
      self.buffer.shift_in(self._cell(position))
    self.buffer.shift_in(C[-1])
    return self.buffer.slice(self.parameters.window_size - length, length)

  def decode_all(self, stream, source_length = 0):
    if len(stream) % self.parameters.Lc != 0:
      raise ValueError('stream length is not a multiple of Lc')
    out = []
    for i in range(0, len(stream), self.parameters.Lc):
      out += self.decode_next(stream[i:i + self.parameters.Lc])
    return out[:source_length] if source_length else out
#--------------------------------------------------

def compress(source, n, buffer_len, lookahead_len, A = None):
  A = sorted(set(source[1:n + 1])) if A is None else sorted(A)
  parameters = make_parameters(len(A), buffer_len, lookahead_len)
  rank = {c: i for i, c in enumerate(A)}
  encoder = Encoder(parameters, [rank[c] for c in source[1:n + 1]])
  return encoder.encode_all(), parameters, A, encoder.stats

def decompress(stream, n, parameters, A):
  return '#' + ''.join(A[s] for s in Decoder(parameters).decode_all(stream, n))
