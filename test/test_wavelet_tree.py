import os
import unittest

from common import wavelet_tree
from generator import rand

class DummySolver:
  def __init__(self, t, n):
    self.t = t
    self.n = n

  def rank(self, c, l ,r):
    if l > r or l > self.n or l < 1:
      return 0
    return sum(1 if x == c else 0 for x in self.t[l:r+1])

  def preifx_rank(self, c, r):
    return self.rank(c, 1, r)

  def select(self, c, k, l, r):
    current_occurrence = 0
    if l > r or l > self.n or l < 1:
      return None
    for i in range(l, r+1):
      if self.t[i] == c:
        current_occurrence = current_occurrence + 1
      if current_occurrence == k:
        return i
    return None

  def quantile(self, k, l, r):
    if l > r or l > self.n or l < 1 or k > r-l+1:
      return None
    substring = self.t[l : r+1]
    return sorted(substring)[k-1]

  def range_count(self, l, r, x, y):
    if l > r or l > self.n or l < 1:
      return None
    result = 0
    for i in range(l, r+1):
      if x <= self.t[i] <= y:
        result = result + 1
    return result

def rank_result(solver, queries):
  return [solver.rank(c, l, r) for (c, l, r) in queries]

def select_result(solver, queries):
  return [solver.select(c, k, l, r) for (c, k, l, r) in queries]

def range_count_result(solver, queries):
  return [solver.range_count(l, r, x, y) for (l, r, x, y) in queries]

def quantile_result(solver, queries):
  return [solver.quantile(k, l, r) for (k, l, r) in queries]

def create_range_for_query(n):
  l = rand.random.randint(1, n)
  r = rand.random.randint(l, n)
  return (l, r)

def create_rank_query(n, alphabet):
  l, r = create_range_for_query(n)
  return (rand.random.choice(alphabet), l, r)

def create_select_query(n, alphabet):
  l, r = create_range_for_query(n)
  return (rand.random.choice(alphabet), rand.random.randint(1, r-l+1), l, r)

# pylint: disable=unused-argument
def create_quantile_query(n, alphabet):
  l, r = create_range_for_query(n)
  return (rand.random.randint(1, r-l+1), l, r)

def create_range_count_query(n, alphabet):
  l, r = create_range_for_query(n)
  x = rand.random.choice(alphabet)
  y = rand.random.choice(alphabet)
  if x > y:
    x, y = y, x
  return (l, r, x, y)


class TestWaveletTree(unittest.TestCase):
  run_large = unittest.skipUnless(
    os.environ.get('LARGE', False), 'Skip test in small runs')

  test_classes = [wavelet_tree.WaveletTree]

  runner_functions = [
    (create_rank_query, rank_result),
    (create_select_query, select_result),
    (create_quantile_query, quantile_result),
    (create_range_count_query, range_count_result)
  ]

  random_small_test_data = [
    (12, 10, ['a', 'b', 'c']),
    (10, 20, ['a', 'b', 'c']),
    (5, 12, ['a', 'b']),
    (7, 12, ['a', 'c']),
    (5, 25, ['a', 'b', 'c', 'd', 'w', 'e'])
  ]

  def create_queries(self, n, q, alphabet, genaration_function):
    return [genaration_function(n, alphabet) for _ in range(q)]

  def test_tree_api_handmade(self):
    # pylint: disable=consider-using-enumerate
    for test_idx in range(len(self.test_inputs)):
      for cls in self.test_classes:
        text, test_cases = self.test_inputs[test_idx]
        solver = cls(text, len(text)-1)
        # pylint: disable=consider-using-enumerate
        for i in range(len(self.runner_functions)):
          _, runner = self.runner_functions[i]
          result = runner(solver, test_cases[i])
          self.assertEqual(self.test_expected_outputs[test_idx][i], result)

  def test_small_random(self):
    for (n, q, alphabet) in self.random_small_test_data:
      self.tree_api_random_test(n, q, alphabet)

  def tree_api_random_test(self, n, q, alphabet):
    text = rand.random_word(n, alphabet)
    model_solver = DummySolver(text, n)
    runners_args = [(runner, self.create_queries(n, q, alphabet, fun))
      for (fun, runner) in self.runner_functions]
    model_results = [runner(model_solver, queries)
      for (runner, queries) in runners_args]
    for cls in self.test_classes:
      solver = cls(text, n)
      results =  [runner(solver, queries) for (runner, queries) in runners_args]
      self.assertEqual(model_results, results)


  large_test_case_data = [
    (1000, 10000, ['a', 'b']),
    (1000, 10000, '''qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM
[];,./?><+_)(*&^%$#@!1234567890-=)'''.split()),
  ]

  @run_large
  def test_large_random(self):
    for (n, q, alphabet) in self.large_test_case_data:
      self.tree_api_random_test(n, q, alphabet)

  test_expected_outputs = [
    [
      [2, 1, 3, 0, 1],
      [3, 5, None, 4, None],
      ['a', 'a', 'a', 'b', None],
      [5, 3, 1, 1, 3, 0, 0]
    ],
    [
      [4, 1, 4, 1, 1, 0, 0, 3, 1, 2, 1, 0],
      [None, None, 3, None, 5, 6, 10, None, None, 7, 8, 10],
      ['c', 'a', 'c', 'a', 'a', 'b', 'b', 'a', 'a', 'c', 'c', 'c'],
      [0, 1, 10, 2, 5, 1, 1, 3, 3, 1, 3, 1]
    ]
  ]

  test_inputs = [
    (
      '#ababa',
      [
        [
          ('a', 1, 3),
          ('b', 1, 3),
          ('a',1 , 5),
          ('c', 1, 5),
          ('a', 3, 3)
        ],
        [
          ('a', 1, 3, 3),
          ('a', 3, 1, 5),
          ('b', 1, 3, 3),
          ('b', 2, 2, 4),
          ('c', 1, 1, 5)
        ],
        [
          (1, 1, 5),
          (1, 3, 3),
          (3, 1, 5),
          (4, 1, 4),
          (2, 1, 1)
        ],
        [
          (1, 5, 'a', 'b'),
          (1, 5, 'a', 'a'),
          (2, 4, 'a', 'a'),
          (3, 3, 'a', 'a'),
          (1, 3, ' ', 'c'),
          (1, 3, ' ', ' '),
          (2, 4, 'c', 'c')
        ]
      ]
    ),
    (
      '#bcbbbaabca',
      [
        [
          ('b', 3, 10),
          ('a', 6, 6),
          ('b', 3, 8),
          ('a', 9, 10),
          ('c', 6, 9),
          ('a', 8, 8),
          ('c', 4, 4),
          ('b', 4, 10),
          ('a', 9, 10),
          ('a', 5, 8),
          ('c', 1, 2),
          ('c', 3, 5)
        ],
        [
          ('c', 2, 8, 10),
          ('c', 2, 4, 5),
          ('b', 1, 3, 9),
          ('c', 1, 5, 8),
          ('b', 1, 5, 5),
          ('a', 1, 5, 8),
          ('a', 1, 10, 10),
          ('c', 6, 3, 8),
          ('a', 1, 3, 3),
          ('a', 2, 6, 9),
          ('b', 4, 3, 9),
          ('a', 1, 10, 10)
        ],
        [
          (1, 9, 9),
          (2, 6, 8),
          (1, 9, 9),
          (2, 6, 8),
          (2, 4, 7),
          (2, 1, 5),
          (2, 4, 6),
          (1, 10, 10),
          (2, 5, 7),
          (2, 1, 2),
          (3, 8, 10),
          (4, 7, 10)
        ],
        [
          (10, 10, 'b', 'b'),
          (3, 3, 'b', 'b'),
          (1, 10, 'a', 'c'),
          (6, 7, 'a', 'c'),
          (1, 6, 'a', 'b'),
          (5, 5, 'a', 'b'),
          (9, 10, 'b', 'c'),
          (3, 7, 'b', 'c'),
          (4, 8, 'b', 'c'),
          (10, 10, 'a', 'b'),
          (4, 6, 'a', 'b'),
          (9, 9, 'a', 'c')
        ]
      ]
    )
  ]
