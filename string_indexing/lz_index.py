#also a bug here
"""def naive_lz78_compress(text):
    text = text[1:]
    text = text + '$' #for last block uniqness
    dictionary = {}
    compressed = []
    phrase = ''
    
    for char in text:
        next_phrase = phrase + char
        exists = dictionary.get(next_phrase)
        if exists is None:
          if phrase == '':
            compressed.append((0, next_phrase[-1]))
            dictionary[next_phrase] = 1
            phrase = ''
          else:
            index = dictionary.get(phrase)
            compressed.append((index, next_phrase[-1]))
            dictionary[next_phrase] = index + 1
            phrase = ''
        else:
          phrase = next_phrase

    return compressed"""

class _LZTreeNode:
  def __init__(self, parent, character, id, position):
    self.parent = parent
    self.position = position
    if parent is not None:
      parent.children[character] = self
      self.depth = parent.depth + 1
    else:
      self.depth = 0
    self.id = id
    self.left_rank = self
    self.right_rank = self
    self.children = {}
    self.character = character

  def set_ranks(self, rank):
    if self.id is not None:
      self.rank = rank
      rank = rank + 1
    else:
      self.rank = None
    if len(self.children) > 0:
      for child_key in sorted(self.children):
        rank = self.children[child_key].set_ranks(rank)
      min_key = min(self.children)
      max_key = max(self.children)
      self.left_rank = self.children[min_key].left_rank \
        if self.rank is None or self.children[min_key].left_rank.rank < self.rank \
        else self
      self.right_rank = self.children[max_key].right_rank \
        if self.rank is None or self.children[max_key].right_rank.rank < self.rank \
        else self
    return rank

  #left rank seems to be useless
  def print_node(self) -> None:
    if self.parent is not None:
      print("(",self.id, ", ", self.parent.id, ", ", self.character, ", ", self.rank, ", ", self.left_rank.rank, ", ", self.right_rank.rank,  "), ")
    for child in self.children.values():
      child.print_node()

  def get_left_rank(self) -> int:
    return self.left_rank.rank
  
  def get_right_rank(self) -> int:
    return self.right_rank.rank
  
  def get_id(self) -> int:
    return self.id
  
  def get_children(self) -> dict:
    return self.children
  


class LZTrieBase:

  def __init__(self) -> None:
    pass

  #normal string with hash at the begining
  def search(self, t, n):
    return self._search_internal(t, n, self.root)

  def _search_internal(self, t, idx, node : _LZTreeNode):
    if idx == 0:
      return node
    if t[idx] not in node.children:
      return None
    return self._search_internal(t, idx - 1, node.children[t[idx]])

  def get_size(self) -> int:
    return self.size

  def debug(self) -> None:
    self.root.print_node()
         
     

class LZTrie(LZTrieBase):
  def __init__(self, t : str, n : int):
    t += '$' #guaranting unique last node
    self.root = _LZTreeNode(None, '#', 0, None)
    current_node = self.root
    id = 1
    for i in range(1, n+1):
      current_char = t[i]
      if current_char not in current_node.children:
        _LZTreeNode(current_node, current_char, id, i)
        id += 1
        current_node = self.root
      else:
        current_node = current_node.children[current_char]
    self.size = id
    self.root.set_ranks(0)

      
class NodeMapper:
  def __init__(self, lz_trie, size):
    self.arr = [None] * size
    self._map_tree_to_list(lz_trie.root)

  def _map_tree_to_list(self, node) -> None:
    if node.id is not None:
      self.arr[node.id] = node
    for child in node.children.values():
      self._map_tree_to_list(child)

  def get_node_by_id(self, id : int) -> _LZTreeNode:
    return self.arr[id]
  
class RangeSearcher:
  def __init__(self, points): 
    self.points = points

  def search_in_range(self, l1, r1, l2, r2):
    result = []
    for (x, y) in self.points:
      if l1 <= x and x <= l2 and r1 <= y and y <= r2:
        result.append((x, y))
    return result


class RevLZTrie(LZTrieBase):

  def __init__(self, lz_trie : LZTrie):
    self.root = _LZTreeNode(None, '#', 0)
    self._add_recursive(lz_trie.root)
    self.root.set_ranks(0)

  def _add_recursive(self, node):
    for child in node.get_children().values():
      self._add_recursive(child)
      self._add_block(child, self.root, child.id)

  def _add_block(self, lz_node : _LZTreeNode, rev_node : _LZTreeNode, id : int) -> None:
    if lz_node.parent is None or lz_node.parent.character is '#':
      if lz_node.character in rev_node.get_children():
        rev_node.children[lz_node.character].id = id
      else:
        rev_node.children[lz_node.character] = _LZTreeNode(rev_node, lz_node.character, id, None)
    else:
      if lz_node.character not in rev_node.get_children():
        rev_node.children[lz_node.character] = _LZTreeNode(rev_node, lz_node.character, None, None)
      self._add_block(lz_node.parent, rev_node.children[lz_node.character], id)

          

class LZIndex:
  def __init__(self, lz_trie : LZTrie, rev_lz_trie : RevLZTrie, node_mapper : NodeMapper, range_searcher : RangeSearcher):
    self.lz_trie = lz_trie
    self.rev_lz_trie = rev_lz_trie
    self.node_mapper = node_mapper
    self.range_searcher = range_searcher

def create_lz_index(t, n):
  lz_trie = LZTrie(t, n)
  rev_trie = RevLZTrie(lz_trie)
  rev_trie.debug()
  lz_node_mapper = NodeMapper(lz_trie, lz_trie.get_size())
  rev_node_mapper = NodeMapper(rev_trie, lz_trie.get_size())

  for node in lz_node_mapper.arr:
    if node.parent is not None:
      print((node.parent.id), node.character)
  points = []
  for i in range(1, lz_trie.get_size() - 1):
    points.append((rev_node_mapper.get_node_by_id(i).rank, lz_node_mapper.get_node_by_id(i+1).rank))
  range_searcher = RangeSearcher(points)
  return LZIndex(lz_trie, rev_trie, rev_node_mapper, range_searcher)

def lz_index_search(lz_index : LZIndex, s, m):

  # single block case
  v = '#' + (s[::-1])[:-1]
  root = lz_index.rev_lz_trie.search(v, m)
  result = []
  for i in range(root.get_left_rank(), root.get_right_rank() + 1):
    node = lz_index.node_mapper.get_node_by_id(i)
    result.append((node.id, m + root.depth - node.depth))
    print("case 1", (node.id, m + root.depth - node.depth))

  # two block case
  for i in range(1, m):
    rev_prefix = '#' + (s[::-1])[m-i:m]
    sufix = '#' + s[i+1:]
    rev_node = lz_index.rev_lz_trie.search(rev_prefix, i)
    node = lz_index.lz_trie.search(sufix, m-i)
    for (x, y) in lz_index.range_searcher.search_in_range(rev_node.get_left_rank(), rev_node.get_right_rank(), node.get_left_rank(), node.get_right_rank()):
      result.append((x, i))
      print("case 2", (x, i))

  # other case
  used = [[False]*(m+1)]*(m+1)
  existance = [[None]*(m+1)]*(m+1)
  arr = [{}]
  for i in range(1, m+1):
    recorded = {}
    current_node = lz_index.lz_trie.root
    for j in range(i, m+1):
      if current_node is not None and s[i] not in current_node.children:
        current_node = None
      elif current_node is not None:
        current_node = current_node.children[s[j]]
      existance[i][j] = current_node
      if current_node is not None:
        recorded[current_node.id] = j
    arr.append(recorded)

  for i in range(1, m+1):
    for j in range(i, m+1):
      if existance[i][j] is None or used[i][j] == True:
        continue
      start_id = existance[i][j].id
      current_id = start_id - 1
      current_end = j - 1
      while current_end < m and (current_id + 1) in arr[current_end+1]:
        current_id = current_id + 1
        used[current_end + 1][arr[current_end + 1][current_id]] = True
        current_end = arr[current_end + 1][current_id]
      size = current_id - start_id  + 1
      if i > 1:
        size = size + 1
      if current_end < m:
        size = size + 1
      if size < 3 or (current_end != m and existance[current_end+1][m] is None):
        continue
      if current_end == m or (existance[current_end+1][m].get_left_rank() <= lz_index.node_mapper.get_node_by_id(current_id + 1) and lz_index.node_mapper.get_node_by_id(current_id + 1) <= existance[current_end+1][m].get_left_rank()):
        if start_id == 1 and i == 1:
          result.append(start_id, i)
          continue
        elif start_id == 1:
          continue
        current_node = lz_index.node_mapper.get_node_by_id(start_id - 1)
        prev = i - 1
        while prev > 0 and current_node.parent != None and s[prev] in current_node.parent.children and current_node.parent.children[s[prev]] == current_node:
          prev = prev - 1
          current_node = current_node.parent
        if prev == 0:
          result.append(start_id - 1, i - 1)
  return result



t = '#aabbababa'
#LZIndex(t) #blocks are not unique in default LZ78 compress (I think it's a bug)
#LZIndex('#aabbababa') #bugged string
#trie = LZTrie(t, len(t)-1)
#trie.debug()

lz_index = create_lz_index(t, len(t) - 1)

print(lz_index_search(lz_index, '#aba', 3))



