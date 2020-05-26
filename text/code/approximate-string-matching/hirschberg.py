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
