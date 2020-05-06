from collections import namedtuple

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
    p_next = d[p].previous
    if p[0] - p_next[0] == 1 and p[1] - p_next[1] == 1:
      text = d[p].letter + text
    p = p_next
  return text, d[(n_1, n_2)].distance
