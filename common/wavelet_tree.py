import itertools

# pylint: disable=too-many-instance-attributes
class WaveletTree:
  def __init__(self, t, n, A = None):
    t = t[1:]
    if A is not None:
      self.alphabet = set(A)
    else:
      self.alphabet = set(t)
      A = sorted(list(self.alphabet))
    self.n, self.smallest, self.largest = n, A[0], A[-1]
    if len(A) == 1:
      self.leaf = True
      return
    self.leaf = False
    A_left, A_right = A[:(len(A) + 1) // 2], A[(len(A) + 1) // 2:]
    self.zero_indexed, self.one_indexed = set(A_left), set(A_right)
    value_array = [1 if c in self.one_indexed else 0 for c in t]
    self.prefix_sum = list(itertools.accumulate(value_array, initial = 0))
    self.left_indices, self.right_indices = [0], [0]
    for i, c in enumerate(t, start = 1):
      if c in self.zero_indexed:
        self.left_indices.append(i)
      else:
        self.right_indices.append(i)
    left_text = ['#'] + [c for c in t if c in self.zero_indexed]
    right_text = ['#'] + [c for c in t if c in self.one_indexed]
    self.left = WaveletTree(left_text, len(left_text) - 1, A_left)
    self.right = WaveletTree(right_text, len(right_text) - 1, A_right)

  def _left_tree_range(self, l, r):
    return l - self.prefix_sum[l - 1], r - self.prefix_sum[r]

  def _right_tree_range(self, l, r):
    return (self.prefix_sum[l - 1] + 1, self.prefix_sum[r])

  def rank(self, c, l, r):
    if c not in self.alphabet or l > r or l > self.n or r < 1:
      return 0
    if self.leaf:
      return r - l + 1
    if c in self.zero_indexed:
      new_l, new_r =  self._left_tree_range(l, r)
      return self.left.rank(c, new_l, new_r)
    new_l, new_r =  self._right_tree_range(l, r)
    return self.right.rank(c, new_l, new_r)

  def prefix_rank(self, c, r):
    return self.rank(c, 1, r)

  def select(self, c, k, l, r):
    if c not in self.alphabet or l > r or l > self.n or r < 1 :
      return None
    if self.leaf:
      return k + l - 1 if k <= r - l + 1 else None
    if c in self.zero_indexed:
      new_l, new_r =  self._left_tree_range(l, r)
      result = self.left.select(c, k, new_l, new_r)
      return self.left_indices[result] if result is not None else None
    new_l, new_r =  self._right_tree_range(l, r)
    result = self.right.select(c, k, new_l, new_r)
    return self.right_indices[result] if result is not None else None

  def quantile(self, k, l, r):
    if k < 1 or k > r - l + 1:
      return None
    if self.leaf:
      return self.smallest if k <= self.n else None
    left_num = self.prefix_sum[r] - self.prefix_sum[l-1]
    if r - l + 1 - left_num >= k:
      new_l, new_r = self._left_tree_range(l, r)
      return self.left.quantile(k, new_l, new_r)
    new_l, new_r =  self._right_tree_range(l, r)
    return self.right.quantile(k-r+l-1+left_num, new_l, new_r)

  def _does_one_range_end_in_another(self, l, r, i, j):
    return (i <= l <= j) or (i <= r <= j)

  def _ranges_intersect(self, l, r, i, j):
    return (self._does_one_range_end_in_another(l, r, i ,j) or
      self._does_one_range_end_in_another(i, j, l, r))

  def range_count(self, l, r, x, y):
    if l > r or l > self.n or l < 1 or x > y:
      return 0
    if x <= self.smallest  and self.largest <= y:
      return r-l+1
    if self.leaf or y < self.smallest or x > self.largest:
      return 0
    l_node, r_node = self.left, self.right
    if (self._ranges_intersect(l_node.smallest, l_node.largest, x, y) and
        self._ranges_intersect(r_node.smallest, r_node.largest, x, y)):
      new_left_l, new_left_r = self._left_tree_range(l, r)
      new_right_l, new_right_r = self._right_tree_range(l, r)
      return (self.left.range_count(new_left_l, new_left_r, x, y)
        + self.right.range_count(new_right_l, new_right_r, x, y))
    if self._ranges_intersect(self.right.smallest, self.right.largest, x, y):
      new_l, new_r = self._right_tree_range(l, r)
      return self.right.range_count(new_l, new_r, x, y)
    new_l, new_r = self._left_tree_range(l, r)
    return self.left.range_count(new_l, new_r, x, y)

  def range_search(self, l, r, x, y):
    if l > r or l > self.n or l < 1 or x > y:
      return []
    if x <= self.smallest and self.largest <= y:
      return list(range(l, r + 1))
    if self.leaf or y < self.smallest or x > self.largest:
      return []
    l_node, r_node = self.left, self.right
    if (self._ranges_intersect(l_node.smallest, l_node.largest, x, y)
        and self._ranges_intersect(r_node.smallest, r_node.largest, x, y)):
      new_left_l, new_left_r = self._left_tree_range(l, r)
      new_right_l, new_right_r = self._right_tree_range(l, r)
      return (([self.left_indices[x] for x in
                 self.left.range_search(new_left_l, new_left_r, x, y)]) +
              ([self.right_indices[x] for x in
                 self.right.range_search(new_right_l, new_right_r, x, y)]))
    if self._ranges_intersect(self.right.smallest, self.right.largest, x, y):
      return [
        self.right_indices[x]
        for x in self.right.range_search(*self._right_tree_range(l, r), x, y)]
    return [
      self.left_indices[x]
      for x in self.left.range_search(*self._left_tree_range(l, r), x, y)]
