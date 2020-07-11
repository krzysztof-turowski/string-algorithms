import itertools
import os
import unittest

import parameterized

from approximate_string_matching import distance, four_russians, linear_space_lcs
from generator import rand

DISTANCE_ALGORITHMS = [
    ['distance', distance.distance],
    # TODO: ['other', linear_space_lcs.distance],
    # TODO: ['four Russians', four_russians.four_russians_distance],
]

class TestDistance(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_distance(self, t_1, t_2, n_1, n_2, reference, S, algorithm):
    self.assertEqual(algorithm(t_1, t_2, n_1, n_2, S), reference, t_1 + ' ' + t_2)

  @parameterized.parameterized.expand(DISTANCE_ALGORITHMS)
  def test_hamming_distance(self, _, algorithm):
    self.check_distance(
        '#GAGGTAGCGGCGTT', '#GTGGTAACGGGGTT', 14, 14, 3,
        distance.HAMMING_DISTANCE, algorithm)

  @parameterized.parameterized.expand(DISTANCE_ALGORITHMS)
  def test_edit_distance(self, _, algorithm):
    self.check_distance(
        '#TGGCCGCGCAAAAACAGC', '#TGACCGCGCAAAACAGC', 18, 17, 2,
        distance.EDIT_DISTANCE, algorithm)
    self.check_distance(
        '#GCGTATGCGGCTAACGC', '#GCTATGCGGCTATACGC', 17, 17, 2,
        distance.EDIT_DISTANCE, algorithm)

  @parameterized.parameterized.expand(DISTANCE_ALGORITHMS)
  @run_large  
  def test_random_hamming_distance(self, _, algorithm):
    T, n, A = 100, 100, ['a', 'b']
    for _ in range(T):
      t_1, t_2 = rand.random_word(n, A), rand.random_word(n, A)
      reference = distance.hamming_distance(t_1, t_2, n, n)
      self.check_distance(
          t_1, t_2, n, n, reference, distance.HAMMING_DISTANCE, algorithm)

  @parameterized.parameterized.expand(DISTANCE_ALGORITHMS)
  @run_large
  def test_all_hamming_distance(self, _, algorithm):
    N, A = 5, ['a', 'b']
    for n in range(3, N + 1):
      for t_1 in itertools.product(A, repeat = n):
        t_1 = '#' + ''.join(t_1)
        for t_2 in itertools.product(A, repeat = n):
          t_2 = '#' + ''.join(t_2)
          reference = distance.hamming_distance(t_1, t_2, n, n)
          self.check_distance(
              t_1, t_2, n, n, reference, distance.HAMMING_DISTANCE, algorithm)

  @parameterized.parameterized.expand(DISTANCE_ALGORITHMS)
  @run_large
  def test_all_indel_distance(self, _, algorithm):
    N_1, N_2, A = 5, 5, ['a', 'b']
    for n_1 in range(3, N_1 + 1):
      for t_1 in itertools.product(A, repeat = n_1):
        t_1 = '#' + ''.join(t_1)
        for n_2 in range(3, N_2 + 1):
          for t_2 in itertools.product(A, repeat = n_2):
            t_2 = '#' + ''.join(t_2)
            reference = distance.distance(
                t_1, t_2, n_1, n_2, distance.INDEL_DISTANCE)
            self.check_distance(
                t_1, t_2, n_1, n_2, reference, distance.INDEL_DISTANCE,
                algorithm)
