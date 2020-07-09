from typing import List, Union
from enum import Enum
from itertools import accumulate

def sa_is(text: str, n: int) -> List[int]:
  '''Computes suffix array using SA-IS algorithm'''
  if n == 0:
    return []

  min_chr = ord(min(text[1:]))
  text_int = [-1] + [ord(c) - min_chr + 1 for c in text[1:]] + [0]

  return _sa_is(text_int, n + 1)[1:]

def _sa_is(text: List[int], n: int) -> List[int]:
  if n == 1:
    return [-1, 1]

  sltext = SLText(text)

  suf = induced_sort(sltext, initial = sltext.lms_pos)
  lms_names = rename_lms_substr(sltext, suf)
  reduced = [-1] + [lms_names[i] for i in sltext.lms_pos]

  reduced_sa = (_sa_is(reduced, len(reduced) - 1)
                if max(reduced) < n-1
                else sa_distinct(reduced))
  ordered_lms = [sltext.lms_pos[i-1] for i in reduced_sa[1:]]

  return induced_sort(sltext, initial = ordered_lms[::-1])

class SLType(Enum):
  L = False
  S = True

class SLText:
  def __init__(self, text: List[int]):
    self.char = text
    self.type = get_ls_types(text)
    self._lms_pos: Union[None, List[int]] = None

  def is_lms(self, i: int) -> bool:
    return i > 1 and (self.type[i-1], self.type[i]) == (SLType.L, SLType.S)

  def lms_eq(self, a: int, b: int) -> bool:
    if a == b:
      return True

    for t in range(0, len(self.char)):
      if self.char[a+t] != self.char[b+t] or self.type[a+t] != self.type[b+t]:
        return False

      if t > 0 and (self.is_lms(a+t) or self.is_lms(b+t)):
        break

    return True

  @property
  def lms_pos(self) -> List[int]:
    if self._lms_pos is None:
      self._lms_pos = [i for i in range(2, len(self.type)) if self.is_lms(i)]
    return self._lms_pos

class BucketDir(Enum):
  FWD = 1
  BWD = -1

class Buckets:
  def __init__(self, target: List[int], sizes: List[int], direction: BucketDir):
    self.target = target
    self.direction = direction
    self.heads = self.find_heads(sizes)

  def find_heads(self, sizes: List[int]) -> List[int]:
    head_dist = [1] + sizes[:-1] if self.direction is BucketDir.FWD else sizes
    return list(accumulate(head_dist))

  def set_and_advance(self, bucket: int, value: int) -> None:
    self.target[self.heads[bucket]] = value
    self.heads[bucket] += self.direction.value

def get_ls_types(text: List[int]) -> List[SLType]:
  types = [SLType.S] * len(text)
  for i in range(len(text) - 2, 0, -1):
    if text[i] == text[i+1]:
      types[i] = types[i+1]
    elif text[i] < text[i+1]:
      types[i] = SLType.S
    else:
      types[i] = SLType.L

  return types

def induced_sort(text: SLText, initial: List[int]) -> List[int]:
  suf = len(text.char) * [-1]
  bkt_sizes = get_bucket_sizes(text.char, max(text.char) + 1)

  bkt = Buckets(suf, bkt_sizes, BucketDir.BWD)
  for i in initial:
    bkt.set_and_advance(text.char[i], i)

  bkt = Buckets(suf, bkt_sizes, BucketDir.FWD)
  for i in range(1, len(text.char)):
    j = suf[i] - 1
    if j > 0 and text.type[j] == SLType.L:
      bkt.set_and_advance(text.char[j], j)

  bkt = Buckets(suf, bkt_sizes, BucketDir.BWD)
  for i in range(len(text.char) - 1, 0, -1):
    j = suf[i] - 1
    if j > 0 and text.type[j] == SLType.S:
      bkt.set_and_advance(text.char[j], j)

  return suf

def get_bucket_sizes(text: List[int], k: int) -> List[int]:
  sizes = [0] * k
  for x in range(1, len(text)):
    sizes[text[x]] += 1

  return sizes

def rename_lms_substr(text: SLText, suf: List[int]) -> List[int]:
  names = len(text.char) * [-1]
  counter = 0
  prev = suf[1]

  for i in filter(text.is_lms, suf[1:]):
    if not text.lms_eq(prev, i):
      counter += 1

    names[i] = counter
    prev = i

  return names

def sa_distinct(text: List[int]) -> List[int]:
  result = [-1] * len(text)
  for (i, c) in enumerate(text[1:]):
    result[c+1] = i

  return result
