import collections

from common import numeric

Params = collections.namedtuple(
    'Params', ['alpha', 'n', 'Ls', 'Lp', 'Ll', 'Lc', 'window_size'])

def make_params(alpha, n, Ls):
  if alpha < 2:
    raise ValueError('alpha >= 2 expected')
  if Ls < 1:
    raise ValueError('Ls >= 1 expected')
  if n - Ls < Ls:
    raise ValueError('n - Ls >= Ls expected')
  Lp = numeric.ceil_log(n - Ls, alpha)
  Ll = numeric.ceil_log(Ls, alpha)
  return Params(alpha, n, Ls, Lp, Ll, 1 + Lp + Ll, n - Ls)

#----------------------------------------------------
# Stats
# pylint: disable=too-few-public-methods
class Stats:
  def __init__(self):
    self.source_symbols, self.words = 0, 0

def compression_ratio(stats, params):
  if stats.source_symbols == 0:
    return 0.0
  return stats.words * params.Lc / stats.source_symbols
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
  max_l, best_p, best_l = m - j, 1, 0
  for i in range(1, j + 1):
    l = 0
    while (l < max_l and ring.at(i - 1 + l) == ring.at(j + l)):
      l += 1
    if l >= best_l:
      best_p, best_l = i, l
  return best_p, best_l

class Encoder:
  def __init__(self, params, source):
    self.params, self.source = params, list(source)
    self.buffer = Ring(params.n)
    self.position, self.encoded, self.stats = 0, 0, Stats()
    for i in range(params.Ls):
      self.buffer.set(params.window_size + i, self._next_symbol())

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
    j = self.params.window_size
    pos, l = _reproducible_extension(self.buffer, j, self.params.n - 1)
    parsed_l = l + 1

    C = (numeric.to_radix(pos - 1, self.params.alpha, self.params.Lp)
         + numeric.to_radix(l, self.params.alpha, self.params.Ll)
         + [self.buffer.at(j + l)])

    for _ in range(parsed_l):
      self.buffer.shift_in(self._next_symbol())

    self.encoded += parsed_l
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
  def __init__(self, params):
    self.params, self.buffer = params, Ring(params.window_size)

  def _cell(self, p):
    return self.buffer.at(p - 1)

  def decode_next(self, C):
    if len(C) != self.params.Lc:
      raise ValueError('codeword of length Lc expected')
    p = numeric.from_radix(C[:self.params.Lp], self.params.alpha) + 1
    l = numeric.from_radix(
      C[self.params.Lp:self.params.Lp + self.params.Ll],
      self.params.alpha) + 1
    if not 1 <= p <= self.params.window_size:
      raise ValueError('pointer out of range')
    if not 1 <= l <= self.params.Ls:
      raise ValueError('length out of range')

    for _ in range(l - 1):
      self.buffer.shift_in(self._cell(p))
    self.buffer.shift_in(C[-1])
    return self.buffer.slice(self.params.window_size - l, l)

  def decode_all(self, stream, source_length = 0):
    if len(stream) % self.params.Lc != 0:
      raise ValueError('stream length is not a multiple of Lc')
    out = []
    for i in range(0, len(stream), self.params.Lc):
      out += self.decode_next(stream[i:i + self.params.Lc])
    return out[:source_length] if source_length else out
#--------------------------------------------------

def compress(source, n, buffer_len, lookahead_len, A = None):
  A = sorted(set(source[1:n + 1])) if A is None else sorted(A)
  params = make_params(len(A), buffer_len, lookahead_len)
  rank = {c: i for i, c in enumerate(A)}
  encoder = Encoder(params, [rank[c] for c in source[1:n + 1]])
  return encoder.encode_all(), params, A, encoder.stats

def decompress(stream, n, params, A):
  return '#' + ''.join(A[s] for s in Decoder(params).decode_all(stream, n))
