from collections import namedtuple
import math

from approximate_string_matching.four_russians_helpers import \
  FourRussiansHelpers, lcs_delete_cost_function, \
  lcs_insert_cost_function, lcs_substitute_cost_function

ScoreMatrix = namedtuple(
    'ScoreMatrix', ['insert', 'delete', 'substitute', 'match'])

def hamming_distance(text_1, text_2, n_1, n_2):
  if n_1 != n_2:
    raise ValueError(
        'Hamming distance is defined only for strings of equal length'
    )
  return sum(ci != cj for ci, cj in zip(text_1[1:], text_2[1:]))

def distance_row(text_1, text_2, _, n_2, S):
  previous_row, current_row = None, range(n_2 + 1)
  for i, ci in enumerate(text_1[1:]):
    previous_row, current_row = current_row, [i + 1] + [None] * n_2
    for j, cj in enumerate(text_2[1:]):
      insertion = previous_row[j + 1] + S.insert(ci)
      deletion = current_row[j] + S.delete(cj)
      if ci != cj:
        substitution = previous_row[j] + S.substitute(ci, cj)
      else:
        substitution = previous_row[j] + S.match(ci)
      current_row[j + 1] = min(insertion, deletion, substitution)
  return current_row

def edit_distance(text_1, text_2, n_1, n_2):
  S = ScoreMatrix(
      insert = lambda ci: 1, delete = lambda ci: 1,
      substitute = lambda ci, cj: 1, match = lambda ci: 0)
  if n_1 >= n_2:
    return distance_row(text_1, text_2, n_1, n_2, S)[-1]
  return distance_row(text_2, text_1, n_2, n_1, S)[-1]

def indel_distance_row(text_1, text_2, n_1, n_2):
  S = ScoreMatrix(
      insert = lambda ci: 1, delete = lambda ci: 1,
      substitute = lambda ci, cj: math.inf, match = lambda ci: 0)
  return distance_row(text_1, text_2, n_1, n_2, S)

def indel_distance(text_1, text_2, n_1, n_2):
  return indel_distance_row(text_1, text_2, n_1, n_2)[-1]

def edit_distance_four_russians(
    text_1, text_2,
    delete_cost_function=lcs_delete_cost_function,
    insert_cost_function=lcs_insert_cost_function,
    substitute_cost_function=lcs_substitute_cost_function):
  """ Algorithm proposed by William J. Masek and Michael S. Paterson,
  using the method of "Four Russians """

  fr = FourRussiansHelpers(delete_cost_function,
                           insert_cost_function,
                           substitute_cost_function)
  m, A, step_size_bound, text_1, text_2 = fr.prepare_parameters(text_1, text_2)
  storage = fr.algorithm_y(m, A, step_size_bound)
  cost = fr.get_edit_distance(m, text_1, text_2, storage)
  return cost
