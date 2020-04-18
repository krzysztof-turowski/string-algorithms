def hamming_distance(text, word, n, m):
  if n != m:
    raise ValueError('Hamming distance is defined only for equal strings')
  return sum(ci != cj for ci, cj in zip(text[1:], word[1:]))

def edit_distance(text, word, n, m):
  if n < m:
    return edit_distance(word, text, m, n)
  previous_row, current_row = None, range(m + 1)
  for i, ci in enumerate(text[1:]):
    previous_row, current_row = current_row, [i + 1] + [None] * m
    for j, cj in enumerate(word[1:]):
      insertion = previous_row[j + 1] + 1
      deletion = current_row[j] + 1
      substitution = previous_row[j] + (ci != cj)
      current_row[j + 1] = min(insertion, deletion, substitution)
  return current_row[-1]
