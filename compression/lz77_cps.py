import collections
import math

from common import numeric
from string_indexing import lcp, suffix_array

Parameters = collections.namedtuple(
    'Parameters', ['alpha', 'n', 'max_length', 'Lp', 'Ll', 'Lc'])

def make_parameters(alpha, n, max_length):
  if alpha < 2:
    raise ValueError('alpha >= 2 expected')
  if n < 0:
    raise ValueError('n >= 0 expected')
  Lp = math.ceil(math.log(n + 1, alpha))
  Ll = math.ceil(math.log(max_length + 1, alpha))
  return Parameters(alpha, n, max_length, Lp, Ll, 1 + Lp + Ll)

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
PosLen = collections.namedtuple('PosLen', ['position', 'length'])

def chen_puglisi_smyth_factorization(w, n, SA = None, LCP = None):
  SA = list(SA) if SA else suffix_array.induced_sorting(w, n)
  LCP = list(LCP) if LCP else lcp.kasai(SA, w, n)
  return _compute_cps_pos_len(SA, LCP, n)

def _compute_cps_pos_len(SA, LCP, n):
  out = PosLen(
    [-1] + list(range(1, n + 1)),
    [-1] + [0] * n)
  if n < 2:
    return out

  sa = [0] * (n + 2)
  lcp_working = [0] * (n + 2)
  for j in range(1, n + 1):
    sa[j] = SA[j]
  for j in range(2, n + 1):
    lcp_working[j] = LCP[j]
  lcp_working[1], lcp_working[n + 1] = -1, -1

  def assign(p, q, l):
    if p < q:
      out.position[q], out.length[q] = p, l
      return p
    out.position[p], out.length[p] = q, l
    return q

  stack = []
  i1, i2, i3 = 1, 2, 3

  while i3 <= n + 1:
    while lcp_working[i2] <= lcp_working[i3]:
      stack.append(i1)
      i1, i2, i3 = i2, i3, i3 + 1

    l2 = lcp_working[i2]
    q = assign(sa[i1], sa[i2], l2)
    while lcp_working[i1] == l2:
      i1 = stack.pop()
      q = assign(sa[i1], q, l2)
    sa[i1] = q

    if i1 > 1:
      i2, i1 = i1, stack.pop()
    else:
      i2, i3 = i3, i3 + 1

  return out

Factor = collections.namedtuple(
  'Factor', ['position', 'length', 'literal'])

def factorize(w, n, POS = None, LEN = None):
  """
  Greedy factorization into Lc
  """
  if POS is None or LEN is None:
    POS, LEN = chen_puglisi_smyth_factorization(w, n)
  factors, i = [], 1
  while i <= n:
    length = LEN[i]
    if i + length > n:
      length = n - i
    factors.append(Factor(POS[i] if length > 0 else 1, length, w[i + length]))
    i += length + 1
  return factors
#----------------------------------------------------

#----------------------------------------------------
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
#----------------------------------------------------

#----------------------------------------------------
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
#----------------------------------------------------

def compress(source, n, A = None):
  A = sorted(set(source[1:n + 1])) if A is None else sorted(A)
  encoder = Encoder(source[:n + 1], n, A)
  return encoder.encode_all(), encoder.parameters, A, encoder.stats

def decompress(stream, n, parameters, A):
  return '#' + ''.join(A[s] for s in Decoder(parameters).decode_all(stream, n))
