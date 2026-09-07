import collections

from common import numeric
from string_indexing import lcp, suffix_array

Params = collections.namedtuple(
    'Params', ['alpha', 'n', 'max_len', 'Lp', 'Ll', 'Lc'])

def make_params(alpha, n, max_len):
  if alpha < 2:
    raise ValueError('alpha >= 2 expected')
  if n < 0:
    raise ValueError('n >= 0 expected')
  Lp = numeric.ceil_log(n, alpha)
  Ll = numeric.ceil_log(max_len + 1, alpha)
  return Params(alpha, n, max_len, Lp, Ll, 1 + Lp + Ll)

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
PosLen = collections.namedtuple('PosLen', ['pos', 'len'])

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
      out.pos[q], out.len[q] = p, l
      return p
    out.pos[p], out.len[p] = q, l
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
  'Factor', ['pos', 'len', 'literal'])

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

    # compute Ll with actual max_len
    max_len = max((f.len for f in self.factors), default = 0)
    self.params = make_params(len(A), n, max_len)
    self.stats.source_symbols = n

  def has_more(self):
    return self.next < len(self.factors)

  def encode_next(self):
    f = self.factors[self.next]
    self.next += 1
    self.stats.words += 1
    return (numeric.to_radix(f.pos - 1, self.params.alpha, self.params.Lp)
            + numeric.to_radix(f.len, self.params.alpha, self.params.Ll)
            + [self.rank[f.literal]])

  def encode_all(self):
    stream = []
    while self.has_more():
      stream += self.encode_next()
    return stream
#----------------------------------------------------

#----------------------------------------------------
# Decoder
class Decoder:
  def __init__(self, params):
    self.params, self.out = params, [-1]

  def decode_next(self, C):
    if len(C) != self.params.Lc:
      raise ValueError('codeword of length Lc expected')
    p = numeric.from_radix(C[:self.params.Lp], self.params.alpha) + 1
    l = numeric.from_radix(
        C[self.params.Lp:self.params.Lp + self.params.Ll],
        self.params.alpha)
    if not 1 <= p <= len(self.out) - 1 and l > 0:
      raise ValueError('pointer out of range')
    if not 0 <= l <= self.params.max_len:
      raise ValueError('length out of range')

    for k in range(l):
      self.out.append(self.out[p + k])
    self.out.append(C[-1])
    return self.out[-(l + 1):]

  def decode_all(self, stream, source_length = 0):
    if len(stream) % self.params.Lc != 0:
      raise ValueError('stream length is not a multiple of Lc')
    for i in range(0, len(stream), self.params.Lc):
      self.decode_next(stream[i:i + self.params.Lc])
    out = self.out[1:]
    return out[:source_length] if source_length else out
#----------------------------------------------------

def compress(source, n, A = None):
  A = sorted(set(source[1:n + 1])) if A is None else sorted(A)
  encoder = Encoder(source[:n + 1], n, A)
  return encoder.encode_all(), encoder.params, A, encoder.stats

def decompress(stream, n, params, A):
  return '#' + ''.join(A[s] for s in Decoder(params).decode_all(stream, n))
