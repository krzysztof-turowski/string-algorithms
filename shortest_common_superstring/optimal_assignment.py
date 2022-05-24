import numpy as np

PRIMED = -1
STARRED = -2

def new_alternating_path(mtx, i, j):
  pos = (i,j)
  path = [pos]
  while True:
    starred_zeros = np.where(mtx.T[pos[1]] == STARRED)[0]
    if len(starred_zeros) == 0:
      break
    pos = (starred_zeros[0], pos[1])
    path.append(pos)
    primed_zero = np.where(mtx[pos[0]] == PRIMED)[0][0]
    pos = (pos[0], primed_zero)
    path.append(pos)
  for pos in path:
    if mtx[pos] == STARRED:
      mtx[pos] = 0
    if mtx[pos] == PRIMED:
      mtx[pos] = STARRED

def cover_zeros(mtx):
  marked_rows, marked_cols = (set(),set())

  for i,row in enumerate(mtx):
    for j,col in enumerate(mtx.T):
      if mtx[i,j] == PRIMED:
        mtx[i,j] = 0
      if mtx[i,j] == STARRED:
        marked_cols.add(j)
      elif mtx[i,j] == 0 and STARRED not in row and STARRED not in col:
        mtx[i,j] = STARRED
        marked_cols.add(j)

  new_prime = True
  while new_prime:
    new_prime = False
    for i,row in enumerate(mtx):
      for j,col in enumerate(mtx.T):
        if mtx[i,j] == 0 and i not in marked_rows and j not in marked_cols:
          mtx[i,j] = PRIMED
          new_prime = True
          if STARRED in row:
            marked_rows.add(i)
            marked_cols.discard(np.where(row == STARRED)[0][0])
          else:
            new_alternating_path(mtx, i, j)
            return cover_zeros(mtx)

  query = np.where(mtx == STARRED)
  marked_zeros = list(zip(query[0],query[1]))
  return (marked_zeros, marked_rows, marked_cols)

def shift_zeros(mtx, marked_rows, marked_cols):
  n = len(mtx)
  min_value = int(1e9)
  for i in range(n):
    for j in range(n):
      if i not in marked_rows and j not in marked_cols:
        min_value = min(min_value, mtx[i,j])
  for i in range(n):
    for j in range(n):
      if i not in marked_rows and j not in marked_cols:
        mtx[i,j] -= min_value
  for i in marked_rows:
    for j in marked_cols:
      mtx[i,j] += min_value
  return mtx

def optimal_assignment(dist_matrix):
  mtx = np.array(dist_matrix)
  n = len(mtx)

  for row in mtx:
    row -= min(row)
  for col in mtx.T:
    col -= min(col)
  lines = 0
  while lines < n:
    marked_zeros, marked_rows, marked_cols = cover_zeros(mtx.copy())
    lines = len(marked_rows) + len(marked_cols)
    if lines < n:
      mtx = shift_zeros(mtx, marked_rows, marked_cols)

  C = [0 for _ in range(n)]
  for pos in marked_zeros:
    C[pos[0]] = pos[1]
  return C
