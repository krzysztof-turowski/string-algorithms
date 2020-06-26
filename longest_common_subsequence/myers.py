from math import ceil

class EditBox:
  def __init__(self, text_a, text_b, a_start, a_end, b_start, b_end):
    self.text_a = text_a
    self.text_b = text_b
    self.a_start = a_start
    self.a_end = a_end
    self.b_start = b_start
    self.b_end = b_end

  def len(self):
    return (self.a_end - self.a_start, self.b_end - self.b_start)

  def compare(self, x, y):
    return self.text_a[x + self.a_start] == self.text_b[y + self.b_start]

  def cut_start(self, x, y):
    return EditBox(
        self.text_a,
        self.text_b,
        self.a_start,
        self.a_start + x,
        self.b_start,
        self.b_start + y
    )

  def cut_end(self, x, y):
    return EditBox(
        self.text_a,
        self.text_b,
        self.a_start + x,
        self.a_end,
        self.b_start + y,
        self.b_end
    )

  def get_first_text(self, start, end):
    return self.text_a[self.a_start + start: self.a_start + end + 1]

  def get_second_text(self):
    return self.text_b[self.b_start + 1:self.b_end + 1]

def _walk_forward(edit_box, d, v_forward, v_backward):
  (a_len, b_len) = edit_box.len()
  delta = a_len - b_len

  for k in range(-d, d + 1, 2):
    if k == -d or (k != d and v_forward[k - 1] < v_forward[k + 1]):
      x = v_forward[k + 1]
    else:
      x = v_forward[k - 1] + 1

    y = x - k

    start = (x,y)
    while x < a_len and y < b_len and edit_box.compare(x + 1, y + 1):
      x, y = x + 1, y + 1
    v_forward[k] = x

    if (delta % 2 == 1 and
        delta -(d - 1) <= k <= delta + (d - 1) and
        y >= v_backward[k - delta]):
      return (start, (x, y))

  return None

def _walk_backward(edit_box, d, v_forward, v_backward):
  (a_len, b_len) = edit_box.len()
  delta = a_len - b_len

  for k in range(-d, d + 1, 2):
    back_k = k + delta
    if k == -d or (k != d and v_backward[k - 1] > v_backward[k + 1]):
      y = v_backward[k + 1]
    else:
      y = v_backward[k - 1] - 1
    x = y + back_k

    start = (x,y)
    while x > 0 and y > 0 and edit_box.compare(x, y):
      x, y = x - 1, y - 1
    v_backward[k] = y

    if (delta % 2 == 0 and
        -d <= back_k <= d and
        x <= v_forward[back_k]):
      return ((x, y), start)

  return None

def _find_middle_snake(edit_box):
  (a_len, b_len) = edit_box.len()
  max_edit = ceil( a_len + b_len / 2)
  v_forward = [0] + [0] * (2 * max_edit)
  v_backward = [0] + [b_len] * (2 * max_edit)
  for d in range(0, max_edit + 1):
    forwardSnake = _walk_forward(edit_box, d, v_forward, v_backward)

    if forwardSnake is not None:
      return (2 * d - 1, forwardSnake)

    backwardSnake = _walk_backward(edit_box, d, v_forward, v_backward)

    if backwardSnake is not None:
      return (2 * d, backwardSnake)

  return None

def _find_lcs(edit_box):
  (a_len, b_len) = edit_box.len()
  if a_len > 0 and b_len > 0:
    (edit_len, ((start_x, start_y), (end_x, end_y))) = (
        _find_middle_snake(edit_box)
    )

    if edit_len > 1:
      left_lcs = _find_lcs(edit_box.cut_start(start_x, start_y))
      middle_lcs = edit_box.get_first_text(start_x + 1, end_x)
      right_lcs = _find_lcs(edit_box.cut_end(end_x, end_y))

      return left_lcs + middle_lcs + right_lcs
    if a_len < b_len:
      return edit_box.get_first_text(1, a_len)
    return edit_box.get_second_text()
  return ''

def longest_common_substring(text_a, text_b, n, m):
  return _find_lcs(EditBox(text_a, text_b, 0, n, 0, m))

def brute_force_lcs(text_a, text_b, n, m):
  vertex_queue = []

  vertex_queue.append((0, 0, ''))
  visited = [[0] * (m + 1) for i in range (n+1)]

  while len(vertex_queue) != 0:
    (x, y, lcs)= vertex_queue.pop(0)
    if x == n and y == m:
      return lcs
    if x != n and visited[x + 1][y] == 0:
      visited[x + 1][y] = 1
      vertex_queue.append((x + 1, y, lcs))
    if y != m and visited[x][y + 1] == 0:
      visited[x][y + 1] = 1
      vertex_queue.append((x, y + 1, lcs))
    if (x != n and y != m and
        text_a[x + 1] == text_b[y + 1] and
        visited[x + 1][y + 1] == 0):
      visited[x + 1][y + 1] = 1
      vertex_queue.append((x + 1, y + 1, lcs + text_a[x + 1]))
