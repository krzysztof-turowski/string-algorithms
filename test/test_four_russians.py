import unittest
from copy import deepcopy

from approximate_string_matching.four_russians_helpers import \
  FourRussiansHelpers, lcs_delete_cost_function, \
  lcs_insert_cost_function, lcs_substitute_cost_function


def substitute_cost_function2(c, d):
  if c == 'a' and d == 'a':
    return 0
  if c == 'b' and d == 'b':
    return 0
  if c == 'a' and d == 'b':
    return 1
  return 2


class TestPrepareParameters(unittest.TestCase):
  def check_prepare_parameters(self, fr, t_1, t_2, expected_m, expected_A,
                               expected_t_1, expected_t_2):
    m, A, step_size_bound, t_1, t_2 = fr.prepare_parameters(t_1, t_2)
    self.assertEqual(m, expected_m)
    self.assertEqual(A, expected_A)
    self.assertEqual(step_size_bound, 1)
    self.assertEqual(t_1, expected_t_1)
    self.assertEqual(t_2, expected_t_2)

  def test_prepare_parameters(self):
    fr = FourRussiansHelpers(lcs_delete_cost_function,
                             lcs_insert_cost_function,
                             lcs_substitute_cost_function)
    self.check_prepare_parameters(fr, "#abab", "#abab",
                                  2, ['a', 'b'],
                                  "#abab", "#abab")
    self.check_prepare_parameters(fr, "#ababa", "#abc",
                                  2, ['a', 'b', 'c'],
                                  "#ababa#", "#abc#")
    self.check_prepare_parameters(fr, "#11111111", "#000",
                                  3, ['0', '1'],
                                  "#11111111#", "#000")


class TestGetAllStrings(unittest.TestCase):
  def check_get_all_strings(self, fr, m, A, dumb_letter, expected_strings):
    strings = fr.get_all_strings(m, A, dumb_letter)
    self.assertEqual(len(strings), len(expected_strings))
    self.assertEqual(strings, expected_strings)

  def test_get_all_strings(self):
    fr = FourRussiansHelpers(lcs_delete_cost_function,
                             lcs_insert_cost_function,
                             lcs_substitute_cost_function)
    self.check_get_all_strings(fr, 2, ['a', 'b'], '#',
                               ["#aa", "#ab", "#ba", "#bb"])
    self.check_get_all_strings(fr, 3, ['z'], '?',
                               ["?zzz"])


class TestStorage(unittest.TestCase):
  def check_storage(self, fr, R_expected_new, S_expected_new,
                    C, D, R, S, storage):
    fr.store(R_expected_new, S_expected_new, C, D, R, S, storage)
    R_new, S_new = fr.fetch(C, D, R, S, storage)
    self.assertEqual(R_expected_new, R_new)
    self.assertEqual(S_expected_new, S_new)

  def test_storage(self):
    fr = FourRussiansHelpers(lcs_delete_cost_function,
                             lcs_insert_cost_function,
                             lcs_substitute_cost_function)
    storage = {}
    self.check_storage(fr, [0, -1], [1, 0], "ab", "ba",
                       [0, 1], [0, -1], storage)
    self.check_storage(fr, [-10, -100], [1, 11], "ababa", "ba",
                       [1, 1], [1, -1], storage)
    self.check_storage(fr, [0, -1], [1, 11], "ababa", "ba",
                       [1, 1], [1, -1], storage)
    self.check_storage(fr, [0, -1], [1, 0], "ab", "ba",
                       [0, 1], [0, -1], storage)


class TestRestoreMatrix(unittest.TestCase):
  def test_restore_matrix(self):
    fr = FourRussiansHelpers(lcs_delete_cost_function,
                             lcs_insert_cost_function,
                             substitute_cost_function2)
    restored_matrix = fr.restore_matrix(
        "#baabab", "#ababaa",
        [0, 1, 2, 3, 4, 5, 6], [0, 1, 2, 3, 4, 5, 6], 6)
    expected_matrix = [[0, 1, 2, 3, 4, 5, 6],
                       [1, 2, 1, 2, 3, 4, 5],
                       [2, 1, 2, 1, 2, 3, 4],
                       [3, 2, 2, 2, 2, 2, 3],
                       [4, 3, 2, 3, 2, 3, 4],
                       [5, 4, 3, 2, 3, 2, 3],
                       [6, 5, 4, 3, 2, 3, 4]]

    self.assertEqual(restored_matrix, expected_matrix)


def get_full_matrices(fr, text_1, text_2, D, I):
  n = len(text_1)

  initial_vertical = [0] * n

  for i in range(1, n):
    initial_vertical[i] = D(text_1[i]) + initial_vertical[i - 1]

  initial_horizontal = [0] * n
  for j in range(1, n):
    initial_horizontal[j] = I(text_2[j]) + initial_horizontal[j - 1]

  whole_matrix = fr.restore_matrix(text_1, text_2,
                                   initial_vertical, initial_horizontal, n - 1)

  diff_between_rows = deepcopy(whole_matrix)
  for i in range(1, n):
    for j in range(0, n):
      diff_between_rows[i][j] = whole_matrix[i][j] - whole_matrix[i - 1][j]

  diff_between_columns = deepcopy(whole_matrix)
  for i in range(0, n):
    for j in range(1, n):
      diff_between_columns[i][j] = whole_matrix[i][j] - whole_matrix[i][j - 1]

  return whole_matrix, diff_between_rows, diff_between_columns


class TestAlgorithmY(unittest.TestCase):
  def test_algorithm_y(self):
    text_1 = "#baabab"
    text_2 = "#ababaa"

    fr = FourRussiansHelpers(lcs_delete_cost_function,
                             lcs_insert_cost_function,
                             substitute_cost_function2)
    m, A, step_size_bound, text_1, text_2 = fr.prepare_parameters(text_1,
                                                                  text_2)
    storage = fr.algorithm_y(m, A, step_size_bound)

    _, diff_between_rows, diff_between_columns = get_full_matrices(
        fr, text_1, text_2,
        lcs_delete_cost_function,
        lcs_insert_cost_function)

    for i in range(0, 5):
      for j in range(0, 5):
        self.assertEqual(storage
                         [text_1[i + 1:i + 3]]
                         [text_2[j + 1:j + 3]]
                         [
                             (diff_between_rows[i + 1][j],
                              diff_between_rows[i + 2][j])
                         ]
                         [
                             (diff_between_columns[i][j + 1],
                              diff_between_columns[i][j + 2])
                         ],
                         (
                             [
                                 diff_between_rows[i + 1][j + 2],
                                 diff_between_rows[i + 2][j + 2]
                             ],
                             [
                                 diff_between_columns[i + 2][j + 1],
                                 diff_between_columns[i + 2][j + 2]
                             ]
                         ))


class TestAlgorithmZ(unittest.TestCase):
  def test_algorithm_z(self):
    text_1 = "#baabab"
    text_2 = "#ababaa"

    fr = FourRussiansHelpers(lcs_delete_cost_function,
                             lcs_insert_cost_function,
                             substitute_cost_function2)
    m, A, step_size_bound, text_1, text_2 = fr.prepare_parameters(text_1,
                                                                  text_2)
    storage = fr.algorithm_y(m, A, step_size_bound)
    P, Q = fr.algorithm_z(m, storage, text_1, text_2)

    _, diff_between_rows, diff_between_columns = get_full_matrices(
        fr, text_1, text_2,
        lcs_delete_cost_function,
        lcs_insert_cost_function)

    for i in range(1, 4):
      for j in range(1, 4):
        self.assertEqual(P[i][j],
                         [diff_between_rows[(i - 1) * m + 1][j * m],
                          diff_between_rows[i * m][j * m]])
        self.assertEqual(Q[i][j],
                         [diff_between_columns[i * m][(j - 1) * m + 1],
                          diff_between_columns[i * m][j * m]])


class TestEditDistance(unittest.TestCase):
  def test_edit_distance(self):
    text_1 = "#baabab"
    text_2 = "#ababaa"

    fr = FourRussiansHelpers(lcs_delete_cost_function,
                             lcs_insert_cost_function,
                             substitute_cost_function2)
    m, A, step_size_bound, text_1, text_2 = fr.prepare_parameters(text_1,
                                                                  text_2)
    storage = fr.algorithm_y(m, A, step_size_bound)
    edit_distance = fr.get_edit_distance(m, text_1, text_2, storage)

    self.assertEqual(edit_distance, 4)


class TestRestoreLcsPart(unittest.TestCase):
  def test_restore_lcs_part(self):
    fr = FourRussiansHelpers(lcs_delete_cost_function,
                             lcs_insert_cost_function,
                             lcs_substitute_cost_function)

    reversed_lcs, i, j = fr.restore_lcs_part(
        "#aa", "#ab",
        [0, 1, 1], [0, 1, 1], 2, 2, 2)
    self.assertEqual(reversed_lcs, "a")
    self.assertEqual(i, 0)
    self.assertEqual(j, 0)

    reversed_lcs, i, j = fr.restore_lcs_part(
        "#aaccc", "#aabc#",
        [0, 1, 1, 1, 1, 1], [0, 1, 1, 1, 1, 1], 5, 5, 5)
    self.assertEqual(reversed_lcs[::-1], "aac")
    self.assertEqual(i, 0)
    self.assertEqual(j, 0)

    reversed_lcs, i, j = fr.restore_lcs_part(
        "#aaa", "#bbb", [0, 1, 1, 1], [0, 1, 1, 1], 3, 3, 3)
    self.assertEqual(reversed_lcs, "")
    self.assertEqual(i, 0)
    self.assertEqual(j, 3)


class TestRestoreLcs(unittest.TestCase):
  def test_restore_lcs_1(self):
    self.check_lcs("#baabab", "#ababaa", "abab")

  def test_restore_lcs_2(self):
    self.check_lcs("#aab", "#baa", "aa")

  def test_restore_lcs_3(self):
    self.check_lcs("#", "#", "")

  def test_restore_lcs_4(self):
    self.check_lcs("#aaa", "#", "")

  def test_restore_lcs_5(self):
    self.check_lcs("#aaa", "#aaa", "aaa")

  def test_restore_lcs_6(self):
    self.check_lcs("#aaab", "#baaa", "aaa")

  def test_restore_lcs_7(self):
    self.check_lcs("#baaba", "#babaa", "baaa")

  def test_restore_lcs_8(self):
    self.check_lcs("#baaa", "#ababaa", "baaa")

  def check_lcs(self, text_1, text_2, expected_lcs):
    expected_length = len(expected_lcs)
    fr = FourRussiansHelpers(lcs_delete_cost_function,
                             lcs_insert_cost_function,
                             lcs_substitute_cost_function)
    m, A, step_size_bound, text_1, text_2 = fr.prepare_parameters(text_1,
                                                                  text_2)
    storage = fr.algorithm_y(m, A, step_size_bound)
    P, Q = fr.algorithm_z(m, storage, text_1, text_2)

    lcs = fr.restore_lcs(text_1, text_2, P, Q, m)
    self.assertEqual(len(lcs), expected_length,
                     "Expected lcs of length {0}, actual lcs of length {1}. "
                     "Actual result: {2}, expected result: {3}"
                     .format(expected_length, len(lcs), lcs, expected_lcs))
    self.assertEqual(lcs, expected_lcs)
