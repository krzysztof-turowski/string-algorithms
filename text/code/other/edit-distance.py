def edit_distance(text_1, text_2, n_1, n_2):
  if n_1 < n_2:
    return edit_distance(text_2, text_1, n_2, n_1)
  previous_row, current_row = None, range(n_2 + 1)
  for i, ci in enumerate(text_1[1:]):
    previous_row, current_row = current_row, [i + 1] + [None] * n_2
    for j, cj in enumerate(text_2[1:]):
      insertion = previous_row[j + 1] + 1
      deletion = current_row[j] + 1
      substitution = previous_row[j] + (ci != cj)
      current_row[j + 1] = min(insertion, deletion, substitution)
  return current_row[-1]
