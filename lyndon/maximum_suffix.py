def from_prefix_suffix(text, n):
  B, t, out = [-1] + [0] * n, -1, 1
  for i in range(1, n + 1):
    # niezmiennik: out = maximum_suffix(text[0..i - 1]))
    # niezmiennik: B[0..i - out] = prefix_suffix(text[out..i - 1])
    # niezmiennik: t = B[i - out]
    while t >= 0 and text[out + t] < text[i]:
      out, t = i - t, B[t]
    while t >= 0 and text[out + t] != text[i]:
      t = B[t]
    t = t + 1
    B[i - out + 1] = t
  return out

def constant_space(text, n):
  out, p, i = 1, 1, 2
  while i <= n:
    r = (i - out) % p
    if text[i] == text[out + r]:
      i = i + 1
    elif text[i] < text[out + r]:
      i, p = i + 1, i + 1 - out
    else:
      out, i, p = i - r, i - r + 1, 1
  return out
