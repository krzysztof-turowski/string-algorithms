import collections
import math
import bisect

from approximate_string_matching import distance

def needleman_wunsch(text_1, text_2, n_1, n_2, S):
  Data = collections.namedtuple('Data', 'distance previousious letter')
  d = { (0, 0): Data(0, None, '') }
  for i, ci in enumerate(text_1[1:]):
    d[(i + 1, 0)] = Data(i + 1, (i, 0), ci)
  for i, ci in enumerate(text_2[1:]):
    d[(0, i + 1)] = Data(i + 1, (0, i), ci)
  for i, ci in enumerate(text_1[1:]):
    for j, cj in enumerate(text_2[1:]):
      if ci == cj:
        substitution = Data(d[(i, j)].distance + S.match(ci), (i, j), ci)
      else:
        substitution = Data(
            d[(i, j)].distance + S.substitute(ci, cj), (i, j), '')
      d[(i + 1, j + 1)] = min(
          Data(d[(i, j + 1)].distance + S.insert(ci), (i, j + 1), ''),
          Data(d[(i + 1, j)].distance + S.delete(cj), (i + 1, j), ''),
          substitution, key = lambda v: v.distance)
  text, p = '', (n_1, n_2)
  while p != (0, 0):
    if p[0] - d[p].previousious[0] == 1 and p[1] - d[p].previousious[1] == 1:
      text = d[p].letter + text
    p = d[p].previousious
  return text

def hirschberg(text_1, text_2, n_1, n_2, S):
  if n_1 < n_2:
    return hirschberg(text_2, text_1, n_2, n_1, S)
  if n_2 == 0:
    return ''
  if n_2 == 1:
    return needleman_wunsch(text_1, text_2, n_1, n_2, S)
  split_1 = n_1 // 2
  distance_previousious = distance.distance_row(
      text_1[:split_1 + 1], text_2, split_1, n_2, S)
  distance_next = distance.distance_row(
      text_1[0] + text_1[n_1:split_1:-1], text_2[0] + text_2[n_2:0:-1],
      n_1 - split_1, n_2, S)[::-1]
  distance_sum = [d_1 + d_2 for d_1, d_2 in zip(
      distance_previousious, distance_next)]
  split_2 = distance_sum.index(min(distance_sum))
  out_previousious = hirschberg(
      text_1[:split_1 + 1], text_2[:split_2 + 1], split_1, split_2, S)
  out_next = hirschberg(
      text_1[0] + text_1[split_1 + 1::], text_2[0] + text_2[split_2 + 1:],
      n_1 - split_1, n_2 - split_2, S)
  return out_previousious + out_next

def _fill_one_row(text_1, text_2, n_2, R1, R2, r, s):
  i, j = s, 1
  R2[0] = n_2 + 1
  while i > 0:
    lower_b, pos_b = 0 if j > r else R1[j], R2[j - 1] - 1
    while pos_b > lower_b and text_1[i - 1] != text_2[pos_b - 1]:
      pos_b = pos_b - 1
    temp = max(pos_b, lower_b)
    if temp == 0:
      break
    R2[j] = temp
    i, j = i - 1, j + 1
  return j - 1

def _call_middle(text_1, text_2, n_1, n_2, x):
  r, LL, R1, R2 = 0, [0] * (n_2 + 1), [0] * (n_2 + 1), [0] * (n_2 + 1)
  for s in range(n_1, n_1 - x - 1, -1):
    r = _fill_one_row(text_1, text_2, n_2, R1, R2, r, s)
    R1[:r + 1] = R2[:r + 1]
  LL[:r + 1] = R1[:r + 1]
  return LL, r

def _solve_base_case(text_1, text_2, n_1, n_2, p):
  LL, _ = _call_middle(text_1, text_2, n_1, n_2, n_1 - p)
  index = next((i for i in range(p) if text_1[i] != text_2[LL[p - i] - 1]), p)
  return text_1[:index] + text_1[index + 1:n_1]

def _find_perfect_cut(text_1, text_2, n_1, n_2, p, w):
  LL1, r_1 = _call_middle(text_1[::-1], text_2[::-1], n_1, n_2, w)
  LL1[:r_1 + 1] = [n_2 + 1 - v for v in LL1[:r_1 + 1]]
  LL2, r_2 = _call_middle(text_1, text_2, n_1, n_2, w)
  k = 0
  for i in range(r_1 + 1):
    if p - i <= r_2 and LL1[i] < LL2[p - i]:
      k = i
  return k + w, LL1[k]

def _lcs(text_1, text_2, n_1, n_2, p):
  w, w_prim = (n_1 - p) // 2, (n_1 - p + 1) // 2
  if n_1 - p <= 1:
    c = _solve_base_case(text_1, text_2, n_1, n_2, p)
  else:
    u, v = _find_perfect_cut(text_1, text_2, n_1, n_2, p, w)
    c = _lcs(text_1[:u], text_2[:v], u, v, u - w) + _lcs(
        text_1[u:], text_2[v:], n_1 - u, n_2 - v, n_1 - u - w_prim)
  return c

def _lcs_length(text_1, text_2, n_1, n_2):
  r, s = 0, n_1 + 1
  R1, R2 = [0] * (n_2 + 1), [0] * (n_2 + 1)
  while s > r:
    r, s = _fill_one_row(text_1, text_2, n_2, R1, R2, r, s - 1), s - 1
    R1[:r + 1] = R2[:r + 1]
  return s

def kumar_rangan(text_1, text_2, n_1, n_2, S):
  # TODO: check if it can be modified for other distance matrices
  if S != distance.INDEL_DISTANCE:
    raise ValueError(
        'Kumar-Rangan algorithm works only for indel/lcs distances')
  p = _lcs_length(text_1[1:], text_2[1:], n_1, n_2)
  return _lcs(text_1[1:], text_2[1:], n_1, n_2, p)

class _EditBox:
  def __init__(self, text_1, text_2, start_1, end_1, start_2, end_2):
    self.text_1, self.start_1, self.end_1 = text_1, start_1, end_1
    self.text_2, self.start_2, self.end_2 = text_2, start_2, end_2

  def len(self):
    return self.end_1 - self.start_1, self.end_2 - self.start_2

  def compare(self, x, y):
    return self.text_1[x + self.start_1] == self.text_2[y + self.start_2]

  def cut_start(self, x, y):
    return _EditBox(self.text_1, self.text_2,
                    self.start_1, self.start_1 + x,
                    self.start_2, self.start_2 + y)

  def cut_end(self, x, y):
    return _EditBox(self.text_1, self.text_2,
                    self.start_1 + x, self.end_1,
                    self.start_2 + y, self.end_2)

  def get_first_text(self, start, end):
    return self.text_1[self.start_1 + start: self.start_1 + end + 1]

  def get_second_text(self):
    return self.text_2[self.start_2 + 1:self.end_2 + 1]

def _walk_forward(edit_box, d, v_forward, v_backward):
  a_len, b_len = edit_box.len()
  delta = a_len - b_len

  for k in range(-d, d + 1, 2):
    if k == -d or (k != d and v_forward[k - 1] < v_forward[k + 1]):
      x = v_forward[k + 1]
    else:
      x = v_forward[k - 1] + 1
    y = x - k

    start = (x, y)
    while x < a_len and y < b_len and edit_box.compare(x + 1, y + 1):
      x, y = x + 1, y + 1
    v_forward[k] = x
    if (delta % 2 == 1 and delta -(d - 1) <= k <= delta + (d - 1)
        and y >= v_backward[k - delta]):
      return (start, (x, y))
  return None

def _walk_backward(edit_box, d, v_forward, v_backward):
  a_len, b_len = edit_box.len()
  delta = a_len - b_len

  for k in range(-d, d + 1, 2):
    back_k = k + delta
    if k == -d or (k != d and v_backward[k - 1] > v_backward[k + 1]):
      y = v_backward[k + 1]
    else:
      y = v_backward[k - 1] - 1
    x = y + back_k

    start = (x, y)
    while x > 0 and y > 0 and edit_box.compare(x, y):
      x, y = x - 1, y - 1
    v_backward[k] = y
    if delta % 2 == 0 and -d <= back_k <= d and x <= v_forward[back_k]:
      return ((x, y), start)
  return None

def _find_middle_snake(edit_box):
  a_len, b_len = edit_box.len()
  max_edit = math.ceil((a_len + b_len) / 2)
  v_forward = [0] + [0] * (2 * max_edit)
  v_backward = [0] + [b_len] * (2 * max_edit)
  for d in range(0, max_edit + 1):
    forward_snake = _walk_forward(edit_box, d, v_forward, v_backward)
    if forward_snake is not None:
      return (2 * d - 1, forward_snake)
    backward_snake = _walk_backward(edit_box, d, v_forward, v_backward)
    if backward_snake is not None:
      return (2 * d, backward_snake)
  raise RuntimeError('This case cannot occur')

def _find_lcs(edit_box):
  a_len, b_len = edit_box.len()
  if a_len > 0 and b_len > 0:
    edit_len, ((start_x, start_y), (end_x, end_y)) = _find_middle_snake(
        edit_box)
    if edit_len > 1:
      left_lcs = _find_lcs(edit_box.cut_start(start_x, start_y))
      middle_lcs = edit_box.get_first_text(start_x + 1, end_x)
      right_lcs = _find_lcs(edit_box.cut_end(end_x, end_y))
      return left_lcs + middle_lcs + right_lcs
    return (edit_box.get_first_text(1, a_len) if a_len < b_len
            else edit_box.get_second_text())
  return ''

def myers(text_1, text_2, n, m, S):
  # TODO: check if it can be modified for other distance matrices
  if S != distance.INDEL_DISTANCE:
    raise ValueError(
        'Myers algorithm works only for indel/lcs distances')
  return _find_lcs(_EditBox(text_1, text_2, 0, n, 0, m))

def _make_matchlists(text_1, text_2, n_1, n_2):
  matchlists = collections.defaultdict(list)
  for j in range(n_2, 0, -1):
    matchlists[text_2[j]].append(j)
  return [None] + [matchlists[text_1[i]] for i in range(1, n_1 + 1)]

def hunt_szymanski(text_1, text_2, n_1, n_2, S):
  """
  Calculates the longest common subsequence of text_1 and text_2
  using the Hunt-Szymanski algorithm.
  Only works with for indel/lcs distance.
  """
  if S != distance.INDEL_DISTANCE:
    raise ValueError(
        'Hunt-Szymanski algorithm works only for indel/lcs distances')
  if n_2 == 0:
    return ""
  matchlist = _make_matchlists(text_1, text_2, n_1, n_2)
  threshold = [0] + [n_2 + 1] * n_2
  link = [None] * (n_2 + 1)
  for i in range(1, n_1 + 1):
    for j in matchlist[i]:
      k = bisect.bisect_left(threshold, j)
      if j < threshold[k]:
        threshold[k], link[k] = j, (i, j, link[k-1])
  k = n_2
  while threshold[k] == n_2 + 1:
    k -= 1
  ptr, result = link[k], []
  while ptr is not None:
    result.append(text_1[ptr[0]])
    ptr = ptr[2]
  return "".join(reversed(result))

def _tree_parent(value):
  """Return the parent of node value"""
  return value // 2

def _tree_left(value):
  """Return the left son of node value"""
  return 2 * value

def _tree_right(value):
  """Return the right son of node value"""
  return 2 * value + 1

class _CTree:
  # pylint: disable-msg=too-many-instance-attributes
  """
  Implementation of Characteristic Trees as described in
  Apostolico, Guerra - The longest common subsequence problem revisited.
  The tree stores a sorted list of numbers from a set universum.
  It maintains pointers to recently accessed leaves to improve performance
  of sequential operations
  ...

  Attributes
  ----------
  universum : list of int
      the universum
  inf : int
      the number to represent infinity
  empty : bool
      whether the starting list is empty

  Methods
  -------
  search(v)
    returns the smallest number u such that u >= v
  insert(v)
    inserts v into the list
  delete(v)
    deletes v from the list
  first()
    returns the smallest number in the list or inf if the list is empty
  """

  def __init__(self, universum, inf, empty=False):
    self.size = 2
    while self.size <= len(universum) + 1:
      self.size *= 2
    self.inf = inf
    self.universum = [0] + universum + [inf] * (self.size - len(universum) - 1)
    self.first_inf = len(universum) + 1
    self.left_max = [0] * (2 * self.size)
    self.right_max = [0] * (2 * self.size)
    self.count = [0] * (2 * self.size)
    self.previous = [None] * (self.size + 1)
    self.next = [None] * (self.size + 1)
    for i in range(self.size, 2 * self.size):
      self.left_max[i] = self.right_max[i] = self.universum[i-self.size]
      self.count[i] = 1 if not empty or i == self.size else 0
    for i in range(self.size-1, 0, -1):
      self.left_max[i] = self.right_max[_tree_left(i)]
      self.right_max[i] = self.right_max[_tree_right(i)]
      self.count[i] = max(self.count[_tree_left(i)], self.count[_tree_right(i)])
    self.next[0] = self.first_inf if empty else 1
    if not empty:
      self.previous[1] = 0
      for i in range(1, len(universum)+1):
        self.next[i] = i + 1
        self.previous[i+1] = i
    self.previous[self.first_inf] = 0 if empty else self.first_inf - 1
    self.search_finger = 0
    self.change_finger = 0

  def _is_leaf(self, value):
    """Return true if node value is a leaf"""
    return value >= self.size

  def _leaf_value(self, value):
    """Return the value at leaf v"""
    return self.universum[value - self.size]

  def _find_neighbor(self, node, value):
    """
    Finds a leaf of a predecessor or successor of value in the tree.
    Returns the node of the largest number p such that p < value
    or the node of the smallest number s >= value.
    It starts searching from leaf it.
    """
    while self.right_max[node] < value or self.count[node] == 0:
      node = _tree_parent(node)
    while not self._is_leaf(node):
      left, right = _tree_left(node), _tree_right(node)
      if self.left_max[node] >= value and \
        self.count[left] > 0 or self.count[right] == 0:
        node = left
      else:
        node = right
    return node

  def _find_exact(self, node, value):
    """
    Returns the leaf corresponding to value in the tree
    It starts searching from leaf node.
    """
    while self.right_max[node] < value:
      node = _tree_parent(node)
    while not self._is_leaf(node):
      node = _tree_left(node) if self.left_max[node] >= value \
        else _tree_right(node)
    return node

  def search(self, value):
    """
    Returns the smallest number u such that u >= value
    """
    if value == self.inf:
      return self.inf
    if self.universum[self.search_finger] > value:
      self.search_finger = 0
    neighbor = self._find_neighbor(self.size + self.search_finger, value)
    if self._leaf_value(neighbor) >= value:
      self.search_finger = neighbor - self.size
      return self._leaf_value(neighbor)
    res = self.next[neighbor - self.size]
    self.search_finger = res
    return self.universum[res]

  def insert(self, value):
    """
    Inserts value into the list
    """
    if value == self.inf:
      return
    if self.universum[self.change_finger] > value:
      self.change_finger = 0

    exact = self._find_exact(self.size + self.change_finger, value)
    predecessor = self._find_neighbor(self.size + self.change_finger, value) - self.size
    if self.universum[predecessor] > value:
      predecessor = self.previous[predecessor]
    successor, leaf = self.next[predecessor], exact - self.size
    self.next[predecessor], self.next[leaf] = leaf, successor
    self.previous[leaf], self.previous[successor] = predecessor, leaf
    self.change_finger, node = leaf, exact
    while self.count[node] == 0:
      self.count[node], node = 1, _tree_parent(node)

  def delete(self, value):
    """
    Deletes value from the list
    """
    if value == self.inf:
      return
    if self.universum[self.change_finger] > value:
      self.change_finger = 0

    exact = self._find_exact(self.size + self.change_finger, value)
    predecessor, successor = self.previous[exact-self.size], self.next[exact-self.size]
    self.next[predecessor], self.previous[successor] = successor, predecessor
    self.change_finger = exact - self.size
    self.count[exact], node = 0, _tree_parent(exact)
    while self.count[node] == 1 and self.count[_tree_left(node)] == 0 \
        and self.count[_tree_right(node)] == 0:
      self.count[node], node = 0, _tree_parent(node)

  def first(self):
    """
    Returns the smallest number in the list or inf if the list is empty
    """
    return self.universum[self.next[0]]

  def __repr__(self):
    res = []
    i = self.next[0]
    while i < self.first_inf:
      res.append(self.universum[i])
      i = self.next[i]
    return f'[{", ".join(map(str, res))}]'

def _make_amatchlists(text_2, n_2):
  amatchlists = collections.defaultdict(list)
  for i in range(1, n_2+1):
    amatchlists[text_2[i]].append(i)
  return {k: _CTree(v, n_2+1) for k, v in amatchlists.items()}

def hunt_szymanski_apostolico(text_1, text_2, n_1, n_2, S):
  # pylint: disable-msg=too-many-locals
  """
  Calculates the longest common subsequence of text_1 and text_2
  using an improved version of the Hunt-Szymanski algorithm.
  Only works with for indel/lcs distance.
  """
  if S != distance.INDEL_DISTANCE:
    raise ValueError(
        'Hunt-Szymanski algorithm works only for indel/lcs distances')
  if n_2 == 0:
    return ""
  # Lists of active matches and thresholds as Characteristic Trees
  amatchlist = _make_amatchlists(text_2, n_2)
  threshold = _CTree(list(range(1, n_2+2)), n_2+1, empty=True)
  # Links used to retrieve the result
  link = [None] * (n_2 + 2)
  # Maintains the values of the matrix in the current row
  rank = [0] * (n_2 + 1) + [1]
  # Current maximum LCS
  max_k = 0
  for i in range(1, n_1 + 1):
    sigma_1 = text_1[i]
    if sigma_1 not in amatchlist:
      continue
    j = amatchlist[sigma_1].first()
    flag, links = True, []
    while flag:
      T = threshold.search(j)
      if T == n_2 + 1:
        flag = False
      k = rank[T]
      # Update the threshold list
      threshold.insert(j)
      threshold.delete(T)
      if j != n_2 + 1:
        # Delay linking to only access values from the previousious row
        links.append((j, k))
        max_k = max(max_k, k)
        rank[j], rank[n_2+1] = k, max_k + 1
      # Remove j from the list of active matches
      amatchlist[sigma_1].delete(j)
      j = amatchlist[sigma_1].search(T)
      # Return T to the list of active matches
      if T != n_2 + 1:
        amatchlist[text_2[T]].insert(T)
    # Update links in the decresing order to only reference
    # links from the previousious row
    for j, k in links[::-1]:
      link[k] = (j, link[k-1])
  # Retrieve the result in the reverse order
  ptr, result = link[max_k], []
  while ptr is not None:
    if ptr[0] <= n_2:
      result.append(text_2[ptr[0]])
    ptr = ptr[1]
  return "".join(reversed(result))
