from collections import namedtuple

from approximate_string_matching import distance
from approximate_string_matching.four_russians_helpers import \
  FourRussiansHelpers, lcs_delete_cost_function, \
  lcs_insert_cost_function, lcs_substitute_cost_function


def needleman_wunsch(text_1, text_2, n_1, n_2):
  Data = namedtuple('Data', ['distance', 'previous', 'letter'])
  d = { (0, 0): Data(0, None, '') }
  for i, ci in enumerate(text_1[1:]):
    d[(i + 1, 0)] = Data(i + 1, (i, 0), ci)
  for i, ci in enumerate(text_2[1:]):
    d[(0, i + 1)] = Data(i + 1, (0, i), ci)
  for i, ci in enumerate(text_1[1:]):
    for j, cj in enumerate(text_2[1:]):
      insertion = Data(d[(i, j + 1)].distance + 1, (i, j + 1), '')
      deletion = Data(d[(i + 1, j)].distance + 1, (i + 1, j), '')
      if ci == cj:
        agreement = Data(d[(i, j)].distance, (i, j), ci)
        if agreement.distance <= min(insertion.distance, deletion.distance):
          d[(i + 1, j + 1)] = agreement
          continue
      if insertion.distance <= deletion.distance:
        d[(i + 1, j + 1)] = insertion
      else:
        d[(i + 1, j + 1)] = deletion
  text, p = '', (n_1, n_2)
  while p != (0, 0):
    if p[0] - d[p].previous[0] == 1 and p[1] - d[p].previous[1] == 1:
      text = d[p].letter + text
    p = d[p].previous
  return text, d[(n_1, n_2)].distance

def hirschberg(text_1, text_2, n_1, n_2):
  if n_1 < n_2:
    return hirschberg(text_2, text_1, n_2, n_1)
  if n_2 == 0:
    return '', n_1
  if n_2 == 1:
    return needleman_wunsch(text_1, text_2, n_1, n_2)
  split_1 = n_1 // 2
  distance_previous = distance.indel_distance_row(
      text_1[:split_1 + 1], text_2, split_1, n_2)
  distance_next = distance.indel_distance_row(
      text_1[0] + text_1[n_1:split_1:-1], text_2[0] + text_2[n_2:0:-1],
      n_1 - split_1, n_2)[::-1]
  distance_sum = [d_1 + d_2 for d_1, d_2 in zip(
      distance_previous, distance_next)]
  split_2 = distance_sum.index(min(distance_sum))
  out_previous = hirschberg(
      text_1[:split_1 + 1], text_2[:split_2 + 1], split_1, split_2)
  out_next = hirschberg(
      text_1[0] + text_1[split_1 + 1::], text_2[0] + text_2[split_2 + 1:],
      n_1 - split_1, n_2 - split_2)
  return out_previous[0] + out_next[0], out_previous[1] + out_next[1]

def four_russians(text_1, text_2):
  """ Calculates longest common subsequence of strings A and B
  as a special case of four russians edit distance algorithm """

  fr = FourRussiansHelpers(
      lcs_delete_cost_function,
      lcs_insert_cost_function,
      lcs_substitute_cost_function)
  m, A, step_size_bound, text_1, text_2 = fr.prepare_parameters(text_1, text_2)
  storage = fr.algorithm_y(m, A, step_size_bound)
  lcs, length = fr.get_lcs(m, text_1, text_2, storage)

  return lcs, length
