def needleman_wunsch(text_1, text_2, n_1, n_2):
  S = { }
  for i in range(n_1 + 1):
    S[(i, 0)] = (i, (0, 0))
  for i in range(1, n_2 + 1):
    S[(0, i)] = (i, (0, 0))
  for i, ci in enumerate(text_1[1:]):
    for j, cj in enumerate(text_2[1:]):
      insertion = (S[(i, j + 1)][0] + 1, (i, j + 1))
      deletion = (S[(i + 1, j)][0] + 1, (i + 1, j))
      if ci == cj:
        agreement = (S[(i, j)][0], (i, j), ci)
        if agreement[0] <= min(insertion[0], deletion[0]):
          S[(i + 1, j + 1)] = agreement
          continue
      if insertion[0] <= deletion[0]:
        S[(i + 1, j + 1)] = insertion
      else:
        S[(i + 1, j + 1)] = deletion
  text, p = '', (n_1, n_2)
  while p != (0, 0):
    p_next = S[p][1]
    if p[0] - p_next[0] == 1 and p[1] - p_next[1] == 1:
      text = S[p][2] + text
    p = p_next
  return text, S[(n_1, n_2)][0]
