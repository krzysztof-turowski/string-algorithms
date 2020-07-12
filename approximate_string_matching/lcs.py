import collections
import math

from approximate_string_matching import distance

def needleman_wunsch(text_1, text_2, n_1, n_2, S):
  Data = collections.namedtuple('Data', 'distance previous letter')
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
    if p[0] - d[p].previous[0] == 1 and p[1] - d[p].previous[1] == 1:
      text = d[p].letter + text
    p = d[p].previous
  return text

def hirschberg(text_1, text_2, n_1, n_2, S):
  if n_1 < n_2:
    return hirschberg(text_2, text_1, n_2, n_1, S)
  if n_2 == 0:
    return ''
  if n_2 == 1:
    return needleman_wunsch(text_1, text_2, n_1, n_2, S)
  split_1 = n_1 // 2
  distance_previous = distance.distance_row(
      text_1[:split_1 + 1], text_2, split_1, n_2, S)
  distance_next = distance.distance_row(
      text_1[0] + text_1[n_1:split_1:-1], text_2[0] + text_2[n_2:0:-1],
      n_1 - split_1, n_2, S)[::-1]
  distance_sum = [d_1 + d_2 for d_1, d_2 in zip(
      distance_previous, distance_next)]
  split_2 = distance_sum.index(min(distance_sum))
  out_previous = hirschberg(
      text_1[:split_1 + 1], text_2[:split_2 + 1], split_1, split_2, S)
  out_next = hirschberg(
      text_1[0] + text_1[split_1 + 1::], text_2[0] + text_2[split_2 + 1:],
      n_1 - split_1, n_2 - split_2, S)
  return out_previous + out_next

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

class EditBox:
  def __init__(self, text_1, text_2, start_1, end_1, start_2, end_2):
    self.text_1, self.start_1, self.end_1 = text_1, start_1, end_1
    self.text_2, self.start_2, self.end_2 = text_2, start_2, end_2

  def len(self):
    return self.end_1 - self.start_1, self.end_2 - self.start_2

  def compare(self, x, y):
    return self.text_1[x + self.start_1] == self.text_2[y + self.start_2]

  def cut_start(self, x, y):
    return EditBox(self.text_1, self.text_2,
                   self.start_1, self.start_1 + x,
                   self.start_2, self.start_2 + y)

  def cut_end(self, x, y):
    return EditBox(self.text_1, self.text_2,
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
  return _find_lcs(EditBox(text_1, text_2, 0, n, 0, m))
