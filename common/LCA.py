import math


# preprocesses tree and handles lca queries
# preprocessing takes O(nlgn) and query answering - O(1)
class LCA:

  def __init__(self):
    self.rmq_array = []
    self.sparse_table = []
    self.first_index_of = {}
    self.depth = {}
    self.internal_indexing = {}
    self.internal_indexing_reversed = {}
    self.internalIndex = 0

  def create_rmq_array(self, node):
    self.rmq_array.append(self.internal_indexing[node.index])
    for child in node.children.values():
      self.create_rmq_array(child)
      self.rmq_array.append(self.internal_indexing[node.index])

  def create_sparse_table(self):
    n = len(self.rmq_array)
    lgn = int(math.log2(n)) + 1
    self.sparse_table = [[-1 for i in range(n)] for i in range(lgn)]
    for i in range(1, n):
      if self.rmq_array[i] > self.rmq_array[i - 1]:
        self.sparse_table[0][i - 1] = i - 1
      else:
        self.sparse_table[0][i - 1] = i
    for j in range(1, lgn):
      for i in range(n - 2 ** (j - 1)):
        s = self.sparse_table[j - 1][i]
        t = self.sparse_table[j - 1][i + 2 ** (j - 1)]
        if self.rmq_array[s] > self.rmq_array[t]:
          self.sparse_table[j][i] = t
        else:
          self.sparse_table[j][i] = s

  def create_first_index_of(self):
    for i in range(len(self.rmq_array)):
      a = self.rmq_array[i]
      if a not in self.first_index_of:
        self.first_index_of[a] = i

  def create_depth(self, node, depth):
    self.depth[node.index] = depth
    for child in node.children.values():
      self.create_depth(child, depth + len(child.label))

  def create_internal_indexing(self, node):
    self.internalIndex += 1
    self.internal_indexing[node.index] = self.internalIndex
    self.internal_indexing_reversed[self.internalIndex] = node.index
    for child in node.children.values():
      self.create_internal_indexing(child)

  def preprocess(self, root):
    self.create_internal_indexing(root)
    self.create_rmq_array(root)
    self.create_sparse_table()
    self.create_first_index_of()
    self.create_depth(root, 0)

  def query_depth(self, a, b):
    return self.depth[self.query(a, b)]

  def query(self, a, b):
    a = self.internal_indexing[a]
    b = self.internal_indexing[b]
    a = self.first_index_of[a]
    b = self.first_index_of[b]
    if a > b:
      tmp = a
      a = b
      b = tmp
    if a == b:
      return self.internal_indexing_reversed[self.rmq_array[a]]
    else:
      d = int(math.log2(b - a))
    if self.rmq_array[self.sparse_table[d][a]] > self.rmq_array[
        self.sparse_table[d][b - 2 ** d]]:
      return self.internal_indexing_reversed[
          self.rmq_array[self.sparse_table[d][b - 2 ** d]]]
    else:
      return self.internal_indexing_reversed[
          self.rmq_array[self.sparse_table[d][a]]]
