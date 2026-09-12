import collections
import math

Parameters = collections.namedtuple('Parameters', ['alpha', 'block_len'])

def make_parameters(alpha, block_len):
  if alpha < 2:
    raise ValueError('alpha >= 2 expected')
  if block_len < 1:
    raise ValueError('block_len >= 1 expected')
  return Parameters(alpha, block_len)

def codeword_width(parameters, j):
  """
  Width in bits of the j-th codeword of a block: ceil(log2(j * alpha))
  """
  return math.ceil(math.log(j * parameters.alpha, 2))

#----------------------------------------------------
# Stats
# @dataclass
class Stats:
  def __init__(self):
    self.source_symbols, self.phrases, self.bits = 0, 0, 0

def compression_ratio(stats, parameters):
  if stats.source_symbols == 0:
    return 0.0
  return stats.bits / (stats.source_symbols * math.log2(parameters.alpha))
#----------------------------------------------------


#----------------------------------------------------
# Bit stream, most significant bit first
BitBuffer = collections.namedtuple('BitBuffer', ['data', 'bits'])

# pylint: disable=too-few-public-methods
class BitWriter:
  def __init__(self):
    self.data, self.bits = bytearray(), 0

  def write(self, value, width):
    for i in range(width - 1, -1, -1):
      if self.bits % 8 == 0:
        self.data.append(0)
      if (value >> i) & 1:
        self.data[-1] |= 1 << (7 - self.bits % 8)
      self.bits += 1

  def buffer(self):
    return BitBuffer(bytes(self.data), self.bits)

# pylint: disable=too-few-public-methods
class BitReader:
  def __init__(self, buffer):
    self.buffer, self.pos = buffer, 0

  def read(self, width):
    if self.pos + width > self.buffer.bits:
      raise ValueError('bit stream does not have this many bits')
    value = 0
    for _ in range(width):
      byte = self.buffer.data[self.pos // 8]
      value = (value << 1) | ((byte >> (7 - self.pos % 8)) & 1)
      self.pos += 1
    return value
#----------------------------------------------------


#----------------------------------------------------
# Dictionary of phrases, a trie stored as parent links
Entry = collections.namedtuple('Entry', ['parent', 'last'])

class Dictionary:
  """
  Node 0 is the empty phrase, every other node is its parent plus one symbol
  """
  def __init__(self):
    self.entries, self.children = [Entry(0, 0)], [{}]

  def reset(self):
    self.entries, self.children = [Entry(0, 0)], [{}]

  def size(self):
    return len(self.entries)

  def child(self, node, s):
    """
    Index of the phrase `node` + `s`, or 0 when it is not in the dictionary
    """
    return self.children[node].get(s, 0)

  def add(self, node, s):
    index = len(self.entries)
    self.entries.append(Entry(node, s))
    self.children.append({})
    self.children[node][s] = index
    return index

  def parent_sequence(self, index):
    """
    Symbols of the phrase stored at `index`, walking the parent links back
    """
    phrase = []
    while index != 0:
      phrase.append(self.entries[index].last)
      index = self.entries[index].parent
    phrase.reverse()
    return phrase
#----------------------------------------------------


#----------------------------------------------------
# Encoder
class Encoder:
  def __init__(self, parameters, source):
    self.parameters, self.source = parameters, list(source)
    self.position, self.j, self.stats = 0, 1, Stats()
    self.dictionary, self.encode_res = Dictionary(), BitWriter()

  def _add_to_bit_buff(self, parent, last):
    """
    I = pi(parent) * alpha + a, written in codeword_width(j) bits
    """
    self.encode_res.write(parent * self.parameters.alpha + last,
                          codeword_width(self.parameters, self.j))
    self.j += 1
    self.stats.phrases += 1

  def has_more(self):
    return self.position < len(self.source)

  def encode_block(self):
    # fallback on the last block
    end = min(self.position + self.parameters.block_len, len(self.source))
    block_symbols = end - self.position

    self.dictionary.reset()
    self.j, current = 1, 0

    while self.position < end:
      s = self.source[self.position]
      self.position += 1
      next = self.dictionary.child(current, s)
      if next != 0:
        current = next
        continue
      self._add_to_bit_buff(current, s)
      self.dictionary.add(current, s)
      current = 0

    # fallback for last match of current block
    if current != 0:
      entry = self.dictionary.entries[current]
      self._add_to_bit_buff(entry.parent, entry.last)

    self.stats.source_symbols += block_symbols
    self.stats.bits = self.encode_res.bits

  def encode_all(self):
    while self.has_more():
      self.encode_block()
    return self.encode_res.buffer()
#---------------------------------------------------


#--------------------------------------------------
#Decoder
# pylint: disable=too-few-public-methods
class Decoder:
  def __init__(self, parameters):
    self.parameters, self.dictionary = parameters, Dictionary()

  def decode_all(self, encoded, source_length):
    reader = BitReader(encoded)
    out = []

    while len(out) < source_length:
      block_symbols = min(self.parameters.block_len, source_length - len(out))
      recreated = 0

      self.dictionary.reset()
      j = 1

      while recreated < block_symbols:
        I = reader.read(codeword_width(self.parameters, j))
        parent, a = divmod(I, self.parameters.alpha)
        phrase = self.dictionary.parent_sequence(parent) + [a]
        out += phrase
        recreated += len(phrase)
        self.dictionary.add(parent, a)
        j += 1

    return out
#--------------------------------------------------

def compress(source, n, block_len, A = None):
  A = sorted(set(source[1:n + 1])) if A is None else sorted(A)
  parameters = make_parameters(len(A), block_len)
  rank = {c: i for i, c in enumerate(A)}
  encoder = Encoder(parameters, [rank[c] for c in source[1:n + 1]])
  return encoder.encode_all(), parameters, A, encoder.stats

def decompress(encoded, n, parameters, A):
  return '#' + ''.join(A[s] for s in Decoder(parameters).decode_all(encoded, n))
