import collections

from approximate_string_matching import distance

def needleman_wunsch(text_1, text_2, n_1, n_2, S):
  Data = collections.namedtuple('Data', 'distance previous letter')
  d = { (0, 0): Data(0, None, '') }
  for i, ci in enumerate(text_1[1:]):
    d[(i + 1, 0)] = Data(i + 1, (i, 0), ci)
  for i, ci in enumerate(text_2[1:]):
    d[(0, i + 1)] = Data(i + 1, (0, i), ci)
  for i, ci in enumerate(text_1[1:]):
    for j, cj in enumerate(text_2[1:]):
      insertion = Data(d[(i, j + 1)].distance + S.insert(ci), (i, j + 1), '')
      deletion = Data(d[(i + 1, j)].distance + S.delete(cj), (i + 1, j), '')
      if ci == cj:
        substitution = Data(d[(i, j)].distance + S.match(ci), (i, j), ci)
      else:
        substitution = Data(
            d[(i, j)].distance + S.substitute(ci, cj), (i, j), '')
      d[(i + 1, j + 1)] = min(
          insertion, deletion, substitution, key = lambda v: v.distance)
  text, p = '', (n_1, n_2)
  while p != (0, 0):
    if p[0] - d[p].previous[0] == 1 and p[1] - d[p].previous[1] == 1:
      text = d[p].letter + text
    p = d[p].previous
  return text, d[(n_1, n_2)].distance

def hirschberg(text_1, text_2, n_1, n_2, S):
  if n_1 < n_2:
    return hirschberg(text_2, text_1, n_2, n_1, S)
  if n_2 == 0:
    return '', n_1
  if n_2 == 1:
    return needleman_wunsch(text_1, text_2, n_1, n_2, S)
  split_1 = n_1 // 2
  distance_previous = distance.distance_row(
      text_1[:split_1 + 1], text_2, split_1, n_2, S)
  distance_next = distance.distance_row(
      text_1[0] + text_1[n_1:split_1:-1], text_2[0] + text_2[n_2:0:-1],
      n_1 - split_1, n_2, S)[::-1]
  distance_sum = [d_1 + d_2 for d_1, d_2 in zip(
      distance_previous, distance_next)]
  split_2 = distance_sum.index(min(distance_sum))
  out_previous = hirschberg(
      text_1[:split_1 + 1], text_2[:split_2 + 1], split_1, split_2, S)
  out_next = hirschberg(
      text_1[0] + text_1[split_1 + 1::], text_2[0] + text_2[split_2 + 1:],
      n_1 - split_1, n_2 - split_2, S)
  return out_previous[0] + out_next[0], out_previous[1] + out_next[1]
