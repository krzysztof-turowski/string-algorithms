from enum import IntEnum
import numpy
import math

class Zero(IntEnum):
  NORMAL = 0
  PRIMED = -1
  STARRED = -2

def new_alternating_path(matrix, i, j):
  position = (i,j)
  path = [position]
  while True:
    starred_zero = next((i for i, v in enumerate(matrix.T[position[1]]) if v == Zero.STARRED), None)
    if starred_zero == None:
      break
    position = (starred_zero, position[1])
    path.append(position)
    primed_zero = next((i for i, v in enumerate(matrix[position[0]]) if v == Zero.PRIMED))
    position = (position[0], primed_zero)
    path.append(position)
  for position in path:
    if matrix[position] == Zero.STARRED:
      matrix[position] = Zero.NORMAL
    elif matrix[position] == Zero.PRIMED:
      matrix[position] = Zero.STARRED

def cover_zeros(matrix):
  marked_rows, marked_cols = (set(),set())

  for i,row in enumerate(matrix):
    for j,col in enumerate(matrix.T):
      if matrix[i,j] == Zero.PRIMED:
        matrix[i,j] = Zero.NORMAL
      if matrix[i,j] == Zero.STARRED:
        marked_cols.add(j)
      elif matrix[i,j] == Zero.NORMAL and Zero.STARRED not in row and Zero.STARRED not in col:
        matrix[i,j] = Zero.STARRED
        marked_cols.add(j)

  new_prime = True
  while new_prime:
    new_prime = False
    for i,row in enumerate(matrix):
      for j,col in enumerate(matrix.T):
        if matrix[i,j] == 0 and i not in marked_rows and j not in marked_cols:
          matrix[i,j] = Zero.PRIMED
          new_prime = True
          if Zero.STARRED in row:
            marked_rows.add(i)
            marked_cols.discard(next((i for i, v in enumerate(row) if v == Zero.STARRED)))
          else:
            new_alternating_path(matrix, i, j)
            return cover_zeros(matrix)

  query = numpy.where(matrix == Zero.STARRED)
  marked_zeros = list(zip(query[0],query[1]))
  return (marked_zeros, marked_rows, marked_cols)

def shift_zeros(matrix, marked_rows, marked_cols):
  n = len(matrix)
  min_value = math.inf
  for i in range(n):
    for j in range(n):
      if i not in marked_rows and j not in marked_cols:
        min_value = min(min_value, matrix[i,j])
  for i in range(n):
    for j in range(n):
      if i not in marked_rows and j not in marked_cols:
        matrix[i,j] -= min_value
  for i in marked_rows:
    for j in marked_cols:
      matrix[i,j] += min_value
  return matrix

def optimal_assignment(dist_matrix):
  matrix = numpy.array(dist_matrix)
  n = len(matrix)
  if n == 1:
    return [0]

  for row in matrix:
    row -= min(row)
  for col in matrix.T:
    col -= min(col)
  lines = 0
  while lines < n:
    marked_zeros, marked_rows, marked_cols = cover_zeros(matrix.copy())
    lines = len(marked_rows) + len(marked_cols)
    if lines < n:
      matrix = shift_zeros(matrix, marked_rows, marked_cols)

  C = [0]*n
  for i,j in marked_zeros:
    C[i] = j
  return C
