import unittest
from copy import deepcopy

from approximate_string_matching import distance, four_russians

TEST_DISTANCE = distance.ScoreMatrix(
    insert = lambda ci: 1, delete = lambda ci: 1,
    match = lambda ci: 0, substitute = lambda ci, cj: 1 if ci < cj else 2)

class TestPrepareParameters(unittest.TestCase):
  def check_prepare_parameters(self, fr, t_1, t_2, n_1, n_2, expected):
    self.assertEqual(fr.prepare_parameters(t_1, t_2, n_1, n_2), expected)

  def test_prepare_parameters(self):
    self.check_prepare_parameters(
        four_russians.FourRussians(distance.INDEL_DISTANCE),
        '#abab', '#abab', 4, 4, (2, ['a', 'b'], 1, '#abab', '#abab'))
    self.check_prepare_parameters(
        four_russians.FourRussians(distance.INDEL_DISTANCE),
        '#ababa', '#abc', 5, 3,
        (2, ['a', 'b', 'c', '$'], 1, '#ababa$', '#abc$'))
    self.check_prepare_parameters(
        four_russians.FourRussians(distance.INDEL_DISTANCE),
        '#aaaaaaaa', '#bbb', 8, 3,
        (3, ['a', 'b', '$'], 1, '#aaaaaaaa$', '#bbb'))

class TestGetAllStrings(unittest.TestCase):
  def check_get_all_strings(self, fr, m, A, dumb_letter, expected_strings):
    strings = fr.get_all_strings(m, A, dumb_letter)
    self.assertEqual(len(strings), len(expected_strings))
    self.assertEqual(strings, expected_strings)

  def test_get_all_strings(self):
    fr = four_russians.FourRussians(distance.INDEL_DISTANCE)
    self.check_get_all_strings(
        fr, 2, ['a', 'b'], '#', ['#aa', '#ab', '#ba', '#bb'])
    self.check_get_all_strings(fr, 3, ['z'], '?', ['?zzz'])

class TestRestoreMatrix(unittest.TestCase):
  def test_restore_matrix(self):
    fr = four_russians.FourRussians(TEST_DISTANCE)
    result = fr.restore_matrix(
        '#baabab', '#ababaa', [0, 1, 2, 3, 4, 5, 6], [0, 1, 2, 3, 4, 5, 6], 6)
    expected = [[0, 1, 2, 3, 4, 5, 6],
                [1, 2, 1, 2, 3, 4, 5],
                [2, 1, 2, 1, 2, 3, 4],
                [3, 2, 2, 2, 2, 2, 3],
                [4, 3, 2, 3, 2, 3, 4],
                [5, 4, 3, 2, 3, 2, 3],
                [6, 5, 4, 3, 2, 3, 4]]
    self.assertEqual(result, expected)

def get_full_matrices(fr, t_1, t_2, S):
  n = len(t_1)

  initial_vertical = [0] * n

  for i in range(1, n):
    initial_vertical[i] = S.delete(t_1[i]) + initial_vertical[i - 1]

  initial_horizontal = [0] * n
  for j in range(1, n):
    initial_horizontal[j] = S.insert(t_2[j]) + initial_horizontal[j - 1]

  whole_matrix = fr.restore_matrix(
      t_1, t_2, initial_vertical, initial_horizontal, n - 1)

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
    t_1 = '#baabab'
    t_2 = '#ababaa'
    n_1, n_2 = 6, 6

    fr = four_russians.FourRussians(TEST_DISTANCE)
    m, A, step, t_1, t_2 = fr.prepare_parameters(t_1, t_2, n_1, n_2)
    storage = fr.algorithm_y(m, A, step)

    _, diff_between_rows, diff_between_columns = get_full_matrices(
        fr, t_1, t_2, TEST_DISTANCE)

    for i in range(0, 5):
      for j in range(0, 5):
        self.assertEqual(
            storage[
                t_1[i + 1:i + 3],
                t_2[j + 1:j + 3],
                (diff_between_rows[i + 1][j],
                 diff_between_rows[i + 2][j]),
                (diff_between_columns[i][j + 1],
                 diff_between_columns[i][j + 2])],
            ([diff_between_rows[i + 1][j + 2],
              diff_between_rows[i + 2][j + 2]],
             [diff_between_columns[i + 2][j + 1],
              diff_between_columns[i + 2][j + 2]]))


class TestAlgorithmZ(unittest.TestCase):
  def test_algorithm_z(self):
    t_1, t_2, n_1, n_2 = '#baabab', '#ababaa', 6, 6
    fr = four_russians.FourRussians(TEST_DISTANCE)
    m, A, step, t_1, t_2 = fr.prepare_parameters(t_1, t_2, n_1, n_2)
    storage = fr.algorithm_y(m, A, step)
    P, Q = fr.algorithm_z(m, storage, t_1, t_2)
    _, diff_between_rows, diff_between_columns = get_full_matrices(
        fr, t_1, t_2, TEST_DISTANCE)

    for i in range(1, 4):
      for j in range(1, 4):
        self.assertEqual(P[i][j],
                         [diff_between_rows[(i - 1) * m + 1][j * m],
                          diff_between_rows[i * m][j * m]])
        self.assertEqual(Q[i][j],
                         [diff_between_columns[i * m][(j - 1) * m + 1],
                          diff_between_columns[i * m][j * m]])

class TestRestoreLcsPart(unittest.TestCase):
  def test_restore_lcs_part(self):
    fr = four_russians.FourRussians(distance.INDEL_DISTANCE)
    self.assertEqual(
        fr.restore_lcs_part('#aa', '#ab',[0, 1, 1], [0, 1, 1], 2, 2, 2),
        ('a', 0, 0))
    self.assertEqual(
        fr.restore_lcs_part(
            '#aaccc', '#aabc#',
            [0, 1, 1, 1, 1, 1], [0, 1, 1, 1, 1, 1], 5, 5, 5),
        ('caa', 0, 0))
    self.assertEqual(
        fr.restore_lcs_part(
            '#aaa', '#bbb', [0, 1, 1, 1], [0, 1, 1, 1], 3, 3, 3),
        ('', 0, 3))
