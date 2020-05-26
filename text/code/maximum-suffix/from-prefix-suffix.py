def from_prefix_suffix(text, n, less = operator.__lt__):
  def equal(a, b):
    return not less(a, b) and not less(b, a)
  B, t, out = [-1] + [0] * n, -1, 1
  for i in range(1, n + 1):
    # niezmiennik: out = maximum_suffix(text[0..i - 1]))
    # niezmiennik: B[0..i - out] = prefix_suffix(text[out..i - 1])
    # niezmiennik: t = B[i - out]
    while t >= 0 and less(text[out + t], text[i]):
      out, t = i - t, B[t]
    while t >= 0 and not equal(text[out + t], text[i]):
      t = B[t]
    t = t + 1
    B[i - out + 1] = t
  return out, (n + 1 - out) - B[n + 1 - out]
