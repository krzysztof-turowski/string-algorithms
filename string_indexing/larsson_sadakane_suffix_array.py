def ternary_sort(I, beginG, endG, V, getKeyForIdx):
  def get_pivot():
    return getKeyForIdx(I[beginG])

  if beginG == endG - 1:
    V[I[beginG] - 1], I[beginG] = beginG, -1
  if endG - beginG < 2:
    return
  pivot = get_pivot()

  fst_eq, last_eq = beginG, beginG + 1

  # parition
  for i in range(beginG + 1, endG):
    key = getKeyForIdx(I[i])
    if key < pivot:
      I[fst_eq], I[i] = I[i], I[fst_eq]
      I[i], I[last_eq] = I[last_eq], I[i]
      fst_eq += 1
      last_eq += 1
    elif key == pivot:
      I[last_eq], I[i] = I[i], I[last_eq]
      last_eq += 1

  ternary_sort(I, beginG, fst_eq, V, getKeyForIdx)

  # update group no and size of the equal part which becomes a group of its own
  if last_eq - fst_eq == 1:
    # we have a new sorted group
    V[I[fst_eq] - 1], I[fst_eq] = fst_eq, -1
  else:
    # process unsorted group
    for i in range(fst_eq, last_eq):
      V[I[i] - 1] = last_eq - 1

  ternary_sort(I, last_eq, endG, V, getKeyForIdx)


def larsson_sadakane_suffix_array(text, n):
  text += '$'
  n += 1
  I = list(range(1, n + 1))

  # STEP 1
  I.sort(key=lambda idx: text[idx])
  h = 1

  # combined STEP 2 & 3
  V = [0] * n
  curr_idx, curr_symbol = n - 1, text[I[n - 1]]
  # Init table V
  for idx, val in enumerate(reversed(I)):
    if curr_symbol != text[val]:
      curr_idx, curr_symbol = n - idx - 1, text[val]
    V[val - 1] = curr_idx

  # Find all groups of size 1 and set their length.
  curr_len, curr_symbol = 0, '$'
  for idx, curr_suff in enumerate(I):
    if curr_symbol != text[curr_suff] and curr_len == 1:
      I[idx - 1] = -1
    if curr_symbol != text[curr_suff]:
      curr_len, curr_symbol = 0, text[curr_suff]
    curr_len += 1

  while h < n and I[0] != -n:
    # scan input, process each unsorted group
    # and merge consecutive combined sorted groups
    i = 0
    while i < n:
      # The group to which suffix_i belongs is combined sorted group.
      # Skip over it (and try to merge with next)
      if I[i] < 0:
        next_i = i - I[i]
        # Merge if next group is also combined sorted group
        while next_i < n and I[next_i] < 0:
          I[i] += I[next_i]
          next_i = i - I[i]
        i = next_i
      else:
        # Run ternary sort
        toSkip = (V[I[i] - 1] - i + 1)
        ternary_sort(I, i, V[I[i] - 1] + 1, V, lambda idx: V[idx + h - 1])
        i += toSkip
    h *= 2

  for i in range(n):
    I[V[i]] = i + 1

  return I
