import math

from approximate_string_matching import distance

class FourRussians:
  def __init__(self, S):
    self.score = distance.ScoreMatrix(
        insert = lambda c: S.insert(c) if c != '$' else 0,
        delete = lambda c: S.delete(c) if c != '$' else 0,
        match = lambda c: S.match(c) if c != '$' else 0,
        substitute = (lambda ci, cj: S.substitute(ci, cj) if '$' not in {ci, cj}
                      else (S.insert(cj) if ci == '$' else S.delete(ci))))

  def prepare_parameters(self, text_1, text_2, n_1, n_2):
    m = int(math.log2(n_1)) if n_1 > 0 else 1
    A = list(sorted(set(c for c in text_1[1:] + text_2[1:])))
    step_size_bound = max(
        max((self.score.insert(c) for c in A), default = 0),
        max((self.score.delete(c) for c in A), default = 0))
    if n_1 % m > 0 or n_2 % m > 0:
      A += ['$']
    text_1 += '$' * ((m - (n_1 % m)) % m)
    text_2 += '$' * ((m - (n_2 % m)) % m)
    return m, A, step_size_bound, text_1, text_2

  @staticmethod
  def get_all_strings(m, A, prefix):
    results = A
    for _ in range(2, m + 1):
      results = [
          left_substring + right_substring
          for left_substring in A for right_substring in results]
    return [prefix + word for word in results]

  def generate_final_step_vectors(self, m, step_vectors, strings):
    storage = {}
    for C in strings:
      for D in strings:
        for R in step_vectors:
          for S in step_vectors:
            T = [[0] * (m + 1) for _ in range(m + 1)]
            U = [[0] * (m + 1) for _ in range(m + 1)]

            for i in range(1, m + 1):
              T[i][0], U[0][i] = R[i], S[i]
            self.compute_next_step_vectors(C, D, T, U, m)
            storage[(C[1:], D[1:], tuple(R[1:]), tuple(S[1:]))] = (
                [T[i][m] for i in range(1, (m + 1))],
                [U[m][i] for i in range(1, (m + 1))])
    return storage

  def compute_next_step_vectors(self, C, D, T, U, m):
    for i in range(1, m + 1):
      for j in range(1, m + 1):
        substitute = (self.score.match(C[i]) if C[i] == D[j]
                      else self.score.substitute(C[i], D[j]))
        T[i][j] = min(
            substitute - U[i - 1][j],
            self.score.delete(C[i]),
            self.score.insert(D[j]) + T[i][j - 1] - U[i - 1][j])
        U[i][j] = min(
            substitute - T[i][j - 1],
            self.score.delete(C[i]) + U[i - 1][j] - T[i][j - 1],
            self.score.insert(D[j]))

  def algorithm_y(self, m, A, step_size_bound):
    strings = self.get_all_strings(m, A, '#')
    step_vectors_alphabet = [
        [cost] for cost in range(-step_size_bound, step_size_bound + 1)]
    step_vectors = self.get_all_strings(m, step_vectors_alphabet, [0])
    return self.generate_final_step_vectors(m, step_vectors, strings)

  @staticmethod
  def get_text_parts(m, text_1):
    return (len(text_1) - 1) // m

  def algorithm_z(self, m, storage, text_1, text_2):
    text_1_parts_bound = self.get_text_parts(m, text_1) + 1
    text_2_parts_bound = self.get_text_parts(m, text_2) + 1
    P = [[[] for _ in range(text_2_parts_bound)]
         for _ in range(text_1_parts_bound)]
    Q = [[[] for _ in range(text_2_parts_bound)]
         for _ in range(text_1_parts_bound)]
    for i in range(1, text_1_parts_bound):
      P[i][0] = [self.score.delete(c)
                 for c in text_1[(i - 1) * m + 1:i * m + 1]]
    for j in range(1, text_2_parts_bound):
      Q[0][j] = [self.score.insert(c)
                 for c in text_2[(j - 1) * m + 1:j * m + 1]]

    for i in range(1, text_1_parts_bound):
      for j in range(1, text_2_parts_bound):
        P[i][j], Q[i][j] = storage[
            text_1[((i - 1) * m + 1):(i * m + 1)],
            text_2[((j - 1) * m + 1):(j * m + 1)],
            tuple(P[i][j - 1]), tuple(Q[i - 1][j])]
    return P, Q

  def restore_matrix(self, C, D, R, S, m):
    M = [[0] * (m + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
      M[i][0], M[0][i] = R[i], S[i]
    for i in range(1, m + 1):
      for j in range(1, m + 1):
        substitute = (self.score.match(C[i]) if C[i] == D[j]
                      else self.score.substitute(C[i], D[j]))
        M[i][j] = min(
            substitute + M[i - 1][j - 1],
            self.score.delete(C[i]) + M[i - 1][j],
            self.score.insert(D[j]) + M[i][j - 1])
    return M

  def restore_lcs_part(self, C, D, R, S, m, i1, j1):
    M = self.restore_matrix(C, D, R, S, m)
    i, j, lcs = i1, j1, ""
    while i != 0 and j != 0:
      if C[i] == D[j]:
        if C[i] not in {'#', '$'}:
          lcs += C[i]
        i, j = i - 1, j - 1
      elif M[i][j] == self.score.delete(C[i]) + M[i - 1][j]:
        i = i - 1
      elif M[i][j] == self.score.insert(D[j]) + M[i][j - 1]:
        j = j - 1
    return lcs, i, j

  def restore_lcs(self, text_1, text_2, P, Q, m):
    I, J = (len(text_1) - 1) // m, (len(text_2) - 1) // m
    i, j, lcs = m, m, ""
    while I != 0 and J != 0:
      C = '#' + text_1[((I - 1) * m + 1):(I * m + 1)]
      D = '#' + text_2[((J - 1) * m + 1):(J * m + 1)]
      lcs_part, i, j = self.restore_lcs_part(
          C, D, [0] + P[I][J - 1], [0] + Q[I - 1][J], m, i, j)
      if i == 0:
        I, i = I - 1, m
      if j == 0:
        J, j = J - 1, m
      lcs += lcs_part

    # reverse result:
    return lcs[::-1]

  def get_distance(self, m, text_1, text_2, storage):
    P, Q = self.algorithm_z(m, storage, text_1, text_2)
    cost = 0
    for i in range(1, self.get_text_parts(m, text_1) + 1):
      cost += sum(P[i][0])
    for j in range(1, self.get_text_parts(m, text_2) + 1):
      cost += sum(Q[(len(text_1) - 1) // m][j])
    return cost

  def get_lcs(self, m, text_1, text_2, storage):
    P, Q = self.algorithm_z(m, storage, text_1, text_2)
    lcs = self.restore_lcs(text_1, text_2, P, Q, m)
    return lcs

def four_russians_distance(text_1, text_2, n_1, n_2, S):
  helper = FourRussians(S)
  m, A, step_size_bound, text_1, text_2 = helper.prepare_parameters(
      text_1, text_2, n_1, n_2)
  storage = helper.algorithm_y(m, A, step_size_bound)
  return helper.get_distance(m, text_1, text_2, storage)

def four_russians_lcs(text_1, text_2, n_1, n_2, S):
  helper = FourRussians(S)
  m, A, step_size_bound, text_1, text_2 = helper.prepare_parameters(
      text_1, text_2, n_1, n_2)
  storage = helper.algorithm_y(m, A, step_size_bound)
  return helper.get_lcs(m, text_1, text_2, storage)
