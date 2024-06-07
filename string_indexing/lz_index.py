
class _LZTreeNode:
  def __init__(self, parent, character, idx, position):
    self.parent = parent
    self.position = position
    if parent is not None:
      parent.children[character] = self
      self.depth = parent.depth + 1
    else:
      self.depth = 0
    self.idx = idx
    self.children = {}
    self.character = character

  def set_ranks(self, rank):
    if self.idx is not None:
      self.rank = rank
      self.left_rank = rank
      self.right_rank = rank
      rank = rank + 1
    else:
      self.rank = None
    if len(self.children) > 0:
      for child_key in sorted(self.children):
        rank = self.children[child_key].set_ranks(rank)
      min_key = min(self.children)
      max_key = max(self.children)
      self.left_rank = self.children[min_key].left_rank \
        if self.rank is None or self.children[min_key].left_rank < self.rank \
        else self.rank
      self.right_rank = self.children[max_key].right_rank \
        if self.rank is None or self.children[max_key].right_rank > self.rank \
        else self.rank
    return rank

#normal string with hash at the begining
def search(tree, t, n):
  return _search_internal(t, 0, n, tree.root)

def _search_internal(t, idx, n, node):
  if idx == n:
    return node
  if t[idx + 1] not in node.children:
    return None
  return _search_internal(t, idx + 1, n, node.children[t[idx + 1]])

class _LZTrie:
  def __init__(self, t, n):
    t += '$' #guaranting unique last node
    self.root = _LZTreeNode(None, '#', 0, None)
    current_node = self.root
    idx, position = 1, 1
    for i in range(1, n+2):
      current_char = t[i]
      if current_char not in current_node.children:
        _LZTreeNode(current_node, current_char, idx, position)
        idx += 1
        current_node = self.root
        position = i+1
      else:
        current_node = current_node.children[current_char]
    self.size = idx
    self.root.set_ranks(0)

class _NodeMapper:
  def __init__(self, lz_trie, size):
    self.arr = [None] * size
    self._map_tree_to_list(lz_trie.root)

  def _map_tree_to_list(self, node) -> None:
    if node.idx is not None:
      self.arr[node.idx] = node
    for child in node.children.values():
      self._map_tree_to_list(child)

  def get_node_by_idx(self, idx):
    return self.arr[idx]

class _RangeSearcher:
  def __init__(self, points):
    self.points = points

  def search_in_range(self, l1, r1, l2, r2):
    result = []
    for (x, y) in self.points:
      if l1 <= x <= r1 and l2 <= y <= r2:
        result.append((x, y))
    return result

class _RankMapper:
  def __init__(self, lz_trie, size):
    self.arr = [None] * size
    self._map_tree_to_list(lz_trie.root)

  def _map_tree_to_list(self, node) -> None:
    if node.rank is not None:
      self.arr[node.rank] = node
    for child in node.children.values():
      self._map_tree_to_list(child)

  def get_node_by_rank(self, rank):
    return self.arr[rank]

class _RevLZTrie:
  def __init__(self, lz_trie):
    self.root = _LZTreeNode(None, '#', 0, None)
    self._add_recursive(lz_trie.root)
    self.root.set_ranks(0)

  def _add_recursive(self, node):
    for child in node.children.values():
      self._add_recursive(child)
      self._add_block(child, self.root, child.idx)

  def _add_block(self, lz_node, rev_node, idx):
    if lz_node.parent is None or lz_node.parent.character == '#':
      if lz_node.character in rev_node.children:
        rev_node.children[lz_node.character].idx = idx
      else:
        rev_node.children[lz_node.character] = _LZTreeNode(rev_node, lz_node.character, idx, None)
    else:
      if lz_node.character not in rev_node.children:
        rev_node.children[lz_node.character] = _LZTreeNode(rev_node, lz_node.character, None, None)
      self._add_block(lz_node.parent, rev_node.children[lz_node.character], idx)

class _LZIndex:
  def __init__(self, lz_trie, rev_lz_trie, lz_node_mapper, rev_lz_node_mapper, \
  range_searcher, lz_rank_mapper, rev_lz_rank_mapper):
    self.lz_trie = lz_trie
    self.rev_lz_trie = rev_lz_trie
    self.lz_node_mapper = lz_node_mapper
    self.range_searcher = range_searcher
    self.rev_lz_node_mapper = rev_lz_node_mapper
    self.lz_rank_mapper = lz_rank_mapper
    self.rev_lz_rank_mapper = rev_lz_rank_mapper

def create_lz_index(t, n):
  lz_trie = _LZTrie(t, n)
  rev_trie = _RevLZTrie(lz_trie)
  lz_node_mapper = _NodeMapper(lz_trie, lz_trie.size)
  rev_node_mapper = _NodeMapper(rev_trie, lz_trie.size)

  points = [(rev_node_mapper.get_node_by_idx(i).rank, lz_node_mapper.get_node_by_idx(i+1).rank) \
  for i in range(1, lz_trie.size - 1)]
  range_searcher = _RangeSearcher(points)
  lz_rank_mapper = _RankMapper(lz_trie, lz_trie.size)
  rev_lz_rank_mapper = _RankMapper(rev_trie, lz_trie.size)
  return _LZIndex(lz_trie, rev_trie, lz_node_mapper, rev_node_mapper, \
  range_searcher, lz_rank_mapper, rev_lz_rank_mapper)

def contains(lz_index, s, m):
  yield from sorted(_contains_internal(lz_index, s, m))

def _contains_internal(lz_index : _LZIndex, s, m):
  # single block case
  v = '#' + (s[::-1])[:-1]
  root = search(lz_index.rev_lz_trie, v, m)
  result = []
  if root is not None:
    for i in range(root.left_rank, root.right_rank + 1):
      rev_node = lz_index.rev_lz_rank_mapper.get_node_by_rank(i)
      node = lz_index.lz_node_mapper.get_node_by_idx(rev_node.idx)
      for j in range(node.left_rank, node.right_rank + 1):
        result_node = lz_index.lz_rank_mapper.get_node_by_rank(j)
        result.append(result_node.position + node.depth - m)

  # two block case
  for i in range(1, m):
    rev_prefix = '#' + (s[::-1])[m-i:m]
    sufix = '#' + s[i+1:]
    rev_node = search(lz_index.rev_lz_trie, rev_prefix, i)
    node = search(lz_index.lz_trie, sufix, m-i)
    if rev_node is None or node is None:
      continue
    for (x, _) in lz_index.range_searcher.search_in_range(rev_node.left_rank, \
    rev_node.right_rank, node.left_rank, node.right_rank):
      rev_node = lz_index.rev_lz_rank_mapper.get_node_by_rank(x)
      node = lz_index.lz_node_mapper.get_node_by_idx(rev_node.idx)
      result.append(node.position + node.depth - i)

  # other case
  used = [[False]*(m+1) for _ in range(m+1)]
  existance = [[None]*(m+1) for _ in range(m+1)]
  arr = [{}]
  for i in range(1, m+1):
    recorded = {}
    current_node = lz_index.lz_trie.root
    for j in range(i, m+1):
      if current_node is not None and s[j] not in current_node.children:
        current_node = None
      elif current_node is not None:
        current_node = current_node.children[s[j]]
      existance[i][j] = current_node
      if current_node is not None:
        recorded[current_node.idx] = j
    arr.append(recorded)

  for i in range(1, m+1):
    for j in range(i, m+1):
      if existance[i][j] is None or used[i][j] is True:
        continue
      start_idx = existance[i][j].idx
      current_idx = start_idx
      current_end = j
      while current_end < m and (current_idx + 1) in arr[current_end+1]:
        current_idx = current_idx + 1
        used[current_end + 1][arr[current_end + 1][current_idx]] = True
        current_end = arr[current_end + 1][current_idx]
      size = current_idx - start_idx  + 1
      if i > 1:
        size = size + 1
      if current_end < m:
        size = size + 1
      if size < 3 or (current_end != m and existance[current_end+1][m] is None):
        continue
      if lz_index.lz_trie.size > current_idx + 1 and \
      ( current_end == m or \
      ( existance[current_end+1][m].left_rank <= \
      lz_index.lz_node_mapper.get_node_by_idx(current_idx + 1).rank <= \
      existance[current_end+1][m].right_rank )):
        if i == 1:
          result.append(lz_index.lz_node_mapper.get_node_by_idx(start_idx).position)
          continue
        if start_idx == 1:
          continue
        current_node = lz_index.lz_node_mapper.get_node_by_idx(start_idx - 1)
        prev = i - 1
        while prev > 0 and current_node.parent is not None and \
        s[prev] in current_node.parent.children and \
        current_node.parent.children[s[prev]] == current_node:
          prev = prev - 1
          current_node = current_node.parent
        if prev == 0:
          node = lz_index.lz_node_mapper.get_node_by_idx(start_idx)
          result.append(node.position - i + 1)
  return sorted(result)
