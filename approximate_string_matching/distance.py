import collections
import math

ScoreMatrix = collections.namedtuple(
    'ScoreMatrix', 'insert delete substitute match')

EDIT_DISTANCE = ScoreMatrix(
    insert = lambda ci: 1, delete = lambda ci: 1,
    substitute = lambda ci, cj: 1, match = lambda ci: 0)
INDEL_DISTANCE = ScoreMatrix(
    insert = lambda ci: 1, delete = lambda ci: 1,
    substitute = lambda ci, cj: 3, match = lambda ci: 0)
HAMMING_DISTANCE = ScoreMatrix(
    insert = lambda ci: math.inf, delete = lambda ci: math.inf,
    substitute = lambda ci, cj: 1, match = lambda ci: 0)

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

def distance(text_1, text_2, n_1, n_2, S):
  if n_1 >= n_2:
    return distance_row(text_1, text_2, n_1, n_2, S)[-1]
  return distance_row(text_2, text_1, n_2, n_1, S)[-1]
