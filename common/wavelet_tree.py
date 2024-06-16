# pylint: disable=too-many-instance-attributes
class WaveletTree:
  def __init__(self, t, n, sorted_alphabet_list = None):
    t = t[1:]
    if sorted_alphabet_list is not None:
      self.alphabet = sorted_alphabet_list
    else:
      self.alphabet = set(t)
      sorted_alphabet_list = sorted(list(self.alphabet))
    self.n = n
    self.smallest = sorted_alphabet_list[0]
    self.biggest = sorted_alphabet_list[-1]
    if len(sorted_alphabet_list) == 1:
      self.leaf = True
      return
    self.leaf = False
    left_alphabet = sorted_alphabet_list[:(len(sorted_alphabet_list) + 1)//2]
    right_alphabet = sorted_alphabet_list[(len(sorted_alphabet_list) + 1)//2:]
    self.zero_indexed = set(left_alphabet)
    self.one_indexed = set(right_alphabet)
    value_arr = [1 if c in self.one_indexed else 0 for c in t ]
    self.prefix_sum = [0]
    for i in range(n):
      self.prefix_sum.append(self.prefix_sum[i] + value_arr[i])
    self.left_indexes = [0]
    self.rigth_indexes = [0]
    for i in range(n):
      if t[i] in self.zero_indexed:
        self.left_indexes.append(i+1)
      else:
        self.rigth_indexes.append(i+1)
    left_text = '#' + ''.join(c for c in t if c in self.zero_indexed)
    rigth_text = '#' + ''.join(c for c in t if c in self.one_indexed)
    self.left = WaveletTree(left_text, len(left_text) - 1, left_alphabet)
    self.right = WaveletTree(rigth_text, len(rigth_text) - 1, right_alphabet)

  def _left_tree_range(self, l, r):
    return l - self.prefix_sum[l-1], r - self.prefix_sum[r]

  def _right_tree_range(self, l, r):
    return (self.prefix_sum[l-1] + 1, self.prefix_sum[r])

  def rank(self, c, l, r):
    if c not in self.alphabet or l > r or l > self.n or r < 1:
      return 0
    if self.leaf:
      return r-l+1
    if c in self.zero_indexed:
      new_l, new_r =  self._left_tree_range(l, r)
      return self.left.rank(c, new_l, new_r)
    new_l, new_r =  self._right_tree_range(l, r)
    return self.right.rank(c, new_l, new_r)

  def preifx_rank(self, c, r):
    return self.rank(c, 1, r)

  def select(self, c, k, l, r):
    if c not in self.alphabet or l > r or l > self.n or r < 1 :
      return None
    if self.leaf:
      return k+l-1 if k <= r-l+1 else None
    if c in self.zero_indexed:
      new_l, new_r =  self._left_tree_range(l, r)
      rec_result = self.left.select(c, k, new_l, new_r)
      return self.left_indexes[rec_result] if rec_result is not None else None
    new_l, new_r =  self._right_tree_range(l, r)
    rec_result = self.right.select(c, k, new_l, new_r)
    return self.rigth_indexes[rec_result] if rec_result is not None else None

  def quantile(self, k, l, r):
    if k < 1 or k > r-l+1:
      return None
    if self.leaf:
      return self.smallest if k <= self.n else None
    left_num = self.prefix_sum[r] - self.prefix_sum[l-1]
    if r-l+1-left_num >= k:
      new_l, new_r =  self._left_tree_range(l, r)
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
    if x <= self.smallest  and self.biggest <= y:
      return r-l+1
    if self.leaf or y < self.smallest or x > self.biggest:
      return 0
    l_node, r_node = self.left, self.right
    if (self._ranges_intersect(l_node.smallest, l_node.biggest, x, y) and
        self._ranges_intersect(r_node.smallest, r_node.biggest, x, y)):
      new_left_l, new_left_r = self._left_tree_range(l, r)
      new_right_l, new_right_r = self._right_tree_range(l, r)
      return (self.left.range_count(new_left_l, new_left_r, x, y)
        + self.right.range_count(new_right_l, new_right_r, x, y))
    if self._ranges_intersect(self.right.smallest, self.right.biggest, x, y):
      new_l, new_r = self._right_tree_range(l, r)
      return self.right.range_count(new_l, new_r, x, y)
    new_l, new_r = self._left_tree_range(l, r)
    return self.left.range_count(new_l, new_r, x, y)
