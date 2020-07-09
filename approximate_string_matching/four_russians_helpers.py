import math

lcs_delete_cost_function = lambda a: 1
lcs_insert_cost_function = lambda b: 1
lcs_substitute_cost_function = lambda a, b: 0 if (a == b) else 2

class FourRussiansHelpers:
  def __init__(
      self,
      delete_cost_function,
      insert_cost_function,
      substitute_cost_function):
    self.delete_cost_function = delete_cost_function
    self.insert_cost_function = insert_cost_function
    self.substitute_cost_function = substitute_cost_function

  def prepare_parameters(self, text_1, text_2):
    A = sorted(list(set(list(text_1[1:] + text_2[1:]))))

    def get_parameter(text_1):
      if len(text_1) == 1:
        return 1
      return int(math.log2(len(text_1) - 1))

    def get_step_size_bound():
      if len(A) == 0:
        return (0, 0)
      I = max(self.insert_cost_function(letter_idx) for letter_idx in A)
      D = max(self.delete_cost_function(letter_idx) for letter_idx in A)
      return max(I, D)

    m = get_parameter(text_1)
    step_size_bound = get_step_size_bound()

    text_1_mod = (len(text_1) - 1) % m
    if text_1_mod != 0:
      text_1 += '#' * (m - (text_1_mod))

    text_2_mod = (len(text_2) - 1) % m
    if text_2_mod != 0:
      text_2 += '#' * (m - (text_2_mod))

    return m, A, step_size_bound, text_1, text_2

  @staticmethod
  def get_all_strings(m, A, dumb_letter):
    """ Returns all possible strings of a given length """

    sub_length_results = [[] for _ in range(m + 1)]
    sub_length_results[1] = A
    for size in range(2, m + 1):
      sub_length_results[size] = [
          left_substring + right_substring
          for left_substring in sub_length_results[1]
          for right_substring in sub_length_results[size - 1]]
    return [dumb_letter + word for word in sub_length_results[m]]

  @staticmethod
  def store(R_new, S_new, C, D, R, S, storage):
    R, S = tuple(R), tuple(S)

    if C not in storage:
      storage[C] = {}
    if D not in storage[C]:
      storage[C][D] = {}
    if R not in storage[C][D]:
      storage[C][D][R] = {}

    storage[C][D][R][S] = (R_new, S_new)

  @staticmethod
  def fetch(C, D, R, S, storage):
    return storage[C][D][tuple(R)][tuple(S)]

  def generate_final_step_vectors(self, m, step_vectors, strings):
    storage = {}

    for C in strings:
      for D in strings:
        for R in step_vectors:
          for S in step_vectors:
            T = [[0] * (m + 1) for _ in range(m + 1)]
            U = [[0] * (m + 1) for _ in range(m + 1)]

            for i in range(1, m + 1):
              T[i][0] = R[i]
              U[0][i] = S[i]

            self.compute_next_step_vectors(C, D, T, U, m)
            R_new = [T[i][m] for i in range(1, (m + 1))]
            S_new = [U[m][i] for i in range(1, (m + 1))]
            self.store(R_new, S_new, C[1:], D[1:], R[1:], S[1:], storage)

    return storage

  def compute_next_step_vectors(self, C, D, T, U, m):
    for i in range(1, m + 1):
      for j in range(1, m + 1):
        T[i][j] = min(
            self.substitute_cost_function(C[i], D[j]) - U[i - 1][j],
            self.delete_cost_function(C[i]),
            self.insert_cost_function(D[j]) + T[i][j - 1] - U[i - 1][j])
        U[i][j] = min(
            self.substitute_cost_function(C[i], D[j]) - T[i][j - 1],
            self.delete_cost_function(C[i]) + U[i - 1][j] - T[i][j - 1],
            self.insert_cost_function(D[j]))

  def algorithm_y(self, m, A, step_size_bound):
    """ Preprocesses data by creating helper submatrices """

    if len(A) == 0:
      return []

    A = ['#'] + A
    strings = self.get_all_strings(m, A, '#')

    step_vectors_alphabet = [[cost] for cost in
                             range(-step_size_bound, step_size_bound + 1)]
    step_vectors = self.get_all_strings(m, step_vectors_alphabet, [0])

    return self.generate_final_step_vectors(m, step_vectors, strings)

  @staticmethod
  def get_text_parts(m, text_1):
    return (len(text_1) - 1) // m

  def algorithm_z(self, m, storage, text_1, text_2):
    """ Returns step vectors needed to calculate the edit distance
    between A and B using preprocessed submatrices of size mxm """

    text_1_parts_bound = self.get_text_parts(m, text_1) + 1
    text_2_parts_bound = self.get_text_parts(m, text_2) + 1

    P = [[[] for _ in range(text_2_parts_bound)] for _ in
         range(text_1_parts_bound)]

    for i in range(1, text_1_parts_bound):
      P[i][0] = [self.delete_cost_function(text_1[letter_idx]) for letter_idx in
                 range((i - 1) * m + 1, i * m + 1)]

    Q = [[[] for _ in range(text_2_parts_bound)] for _ in
         range(text_1_parts_bound)]

    for j in range(1, text_2_parts_bound):
      Q[0][j] = [self.insert_cost_function(text_2[letter_idx]) for letter_idx in
                 range((j - 1) * m + 1, j * m + 1)]

    for i in range(1, text_1_parts_bound):
      for j in range(1, text_2_parts_bound):
        (P[i][j], Q[i][j]) = self.fetch(
            self.get_kth_substring(i, m, text_1),
            self.get_kth_substring(j, m, text_2),
            P[i][j - 1], Q[i - 1][j],
            storage)

    return P, Q

  def restore_matrix(self, C, D, R, S, m):
    M = [[0] * (m + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
      M[i][0] = R[i]
      M[0][i] = S[i]
    for i in range(1, m + 1):
      for j in range(1, m + 1):
        M[i][j] = min(
            self.substitute_cost_function(C[i], D[j]) + M[i - 1][j - 1],
            self.delete_cost_function(C[i]) + M[i - 1][j],
            self.insert_cost_function(D[j]) + M[i][j - 1]
        )
    return M

  def restore_lcs_part(self, C, D, R, S, m, i1, j1):
    M = self.restore_matrix(C, D, R, S, m)

    i, j, lcs = i1, j1, ""
    while i != 0 and j != 0:
      if C[i] == D[j]:
        if C[i] != '#':
          lcs += C[i]
        i, j = i - 1, j - 1
      elif M[i][j] == self.delete_cost_function(C[i]) + M[i - 1][j]:
        i = i - 1
      elif M[i][j] == self.insert_cost_function(D[j]) + M[i][j - 1]:
        j = j - 1
    return lcs, i, j

  @staticmethod
  def get_kth_substring(k, m, text_1):
    return text_1[((k - 1) * m + 1):(k * m + 1)]

  def restore_lcs(self, text_1, text_2, P, Q, m):
    # indices on the matrix of submatrices
    I, J = (len(text_1) - 1) // m, (len(text_2) - 1) // m

    # indices inside of the submatrices
    i, j, lcs = m, m, ""

    while I != 0 and J != 0:
      C = '#' + self.get_kth_substring(I, m, text_1)
      D = '#' + self.get_kth_substring(J, m, text_2)

      lcs_part, i, j = self.restore_lcs_part(
          C, D,
          [0] + P[I][J - 1],
          [0] + Q[I - 1][J],
          m, i, j)

      if i == 0:
        I, i = I - 1, m
      if j == 0:
        J, j = J - 1, m
      lcs += lcs_part

    # reverse result:
    return lcs[::-1]

  def get_edit_distance(self, m, text_1, text_2, storage):
    P, Q = self.algorithm_z(m, storage, text_1, text_2)

    cost = 0

    for i in range(1, self.get_text_parts(m, text_1) + 1):
      cost += sum(P[i][0])

    for j in range(1, self.get_text_parts(m, text_2) + 1):
      cost += sum(Q[int(len(text_1) / m)][j])

    return cost

  def get_lcs(self, m, text_1, text_2, storage):
    if len(text_1) == 0 or len(text_2) == 0:
      return 0, ""

    P, Q = self.algorithm_z(m, storage, text_1, text_2)
    lcs = self.restore_lcs(text_1, text_2, P, Q, m)
    return lcs, len(lcs)
