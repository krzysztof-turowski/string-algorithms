import math

# LCA with preprocessing time O(n log n) and query answering time O(1)
class LCA:
  def __init__(self, root):
    self.rmq_array, self.sparse_table = [], []
    self.first_index_of, self.depth = {}, {}
    self.internal_indexing = {}
    self.internal_indexing_reversed = {}
    self.internal_index = 0
    self._preprocess(root)

  def _preprocess(self, root):
    self._create_internal_indexing(root)
    self._create_rmq_array(root)
    self._create_sparse_table()
    self._create_first_index_of()
    self._create_depth(root, 0)

  def _create_rmq_array(self, node):
    self.rmq_array.append(self.internal_indexing[node.index])
    for child in node.children.values():
      self._create_rmq_array(child)
      self.rmq_array.append(self.internal_indexing[node.index])

  def _create_sparse_table(self):
    n = len(self.rmq_array)
    lgn = int(math.log2(n)) + 1
    self.sparse_table = [[-1 for _ in range(n)] for _ in range(lgn)]
    self.sparse_table[0][:-1] = [
        i if self.rmq_array[i + 1] > self.rmq_array[i] else i + 1
        for i in range(n - 1)
    ]
    for j in range(lgn - 1):
      for i in range(n - 2 ** j):
        s = self.sparse_table[j][i]
        t = self.sparse_table[j][i + 2 ** j]
        if self.rmq_array[s] > self.rmq_array[t]:
          self.sparse_table[j + 1][i] = t
        else:
          self.sparse_table[j + 1][i] = s

  def _create_first_index_of(self):
    for i, a in enumerate(self.rmq_array):
      if a not in self.first_index_of:
        self.first_index_of[a] = i

  def _create_depth(self, node, depth):
    self.depth[node.index] = depth
    for child in node.children.values():
      self._create_depth(child, depth + len(child.label))

  def _create_internal_indexing(self, node):
    self.internal_index += 1
    self.internal_indexing[node.index] = self.internal_index
    self.internal_indexing_reversed[self.internal_index] = node.index
    for child in node.children.values():
      self._create_internal_indexing(child)

  def query_depth(self, a, b):
    return self.depth[self.query(a, b)]

  def query(self, a, b):
    a = self.first_index_of[self.internal_indexing[a]]
    b = self.first_index_of[self.internal_indexing[b]]
    if a == b:
      return self.internal_indexing_reversed[self.rmq_array[a]]
    a, b = min(a, b), max(a, b)
    d = int(math.log2(b - a))
    return self.internal_indexing_reversed[
        min(self.rmq_array[self.sparse_table[d][a]],
            self.rmq_array[self.sparse_table[d][b - 2 ** d]])]
