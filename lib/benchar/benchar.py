class Benchar:
  def __init__(self):
    self.cmp_count = 0

  def __call__(self, *args, **kwargs):
    base_str = str(*args, **kwargs)
    return _CountString(base_str, self)

  @staticmethod
  def first_difference(a, b):
    for i, (u, v) in enumerate(zip(a, b), start = 1):
      if str.__ne__(u, v):
        return i
    return min(len(a), len(b))

class _CountString(str):
  def __new__(cls, base_str, parent_benchar):
    obj = str.__new__(cls, base_str)
    obj._parent_benchar = parent_benchar
    return obj

  def __getitem__(self, key):
    obj = _CountString(str.__getitem__(self, key), self._parent_benchar)
    return obj

  def __add__(self, other):
    obj = _CountString(str.__add__(self, other), self._parent_benchar)
    return obj

  def __radd__(self, other):
    obj = _CountString(str.__add__(other, self), self._parent_benchar)
    return obj

  def __iter__(self):
    obj = _CountStringIterator(str.__iter__(self), self._parent_benchar)
    return obj

  def __eq__(self, other):
    res = str.__eq__(self, other)
    self._parent_benchar.cmp_count += Benchar.first_difference(self, other)
    return res

  def __ne__(self, other):
    res = str.__ne__(self, other)
    self._parent_benchar.cmp_count += Benchar.first_difference(self, other)
    return res

  def __lt__(self, other):
    res = str.__lt__(self, other)
    self._parent_benchar.cmp_count += Benchar.first_difference(self, other)
    return res

  def __le__(self, other):
    res = str.__le__(self, other)
    self._parent_benchar.cmp_count += Benchar.first_difference(self, other)
    return res

  def __gt__(self, other):
    res = str.__gt__(self, other)
    self._parent_benchar.cmp_count += Benchar.first_difference(self, other)
    return res

  def __ge__(self, other):
    res = str.__ge__(self, other)
    self._parent_benchar.cmp_count += Benchar.first_difference(self, other)
    return res

  def endswith(self, other):
    res = str.endswith(self, other)
    if len(self) >= len(other):
      self._parent_benchar.cmp_count += Benchar.first_difference(
        self[-len(other):], other)
    return res

  def startswith(self, other):
    res = str.startswith(self, other)
    if len(self) >= len(other):
      self._parent_benchar.cmp_count += Benchar.first_difference(
        self[:len(other)], other)
    return res

  def __hash__(self):
    res = str.__hash__(self)
    return res

class _CountStringIterator:
  def __init__(self, base_string_iterator, parent_benchar):
    self.base_string_iterator = base_string_iterator
    self._parent_benchar = parent_benchar

  def __iter__(self):
    return self.base_string_iterator.__iter__()

  def __next__(self):
    res = _CountString(
      self.base_string_iterator.__next__(), self._parent_benchar)
    return res
