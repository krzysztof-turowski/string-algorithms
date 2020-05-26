def constant_space(text, n, less = operator.__lt__):
  def equal(a, b):
    return not less(a, b) and not less(b, a)
  out, p, i = 1, 1, 2
  while i <= n:
    r = (i - out) % p
    if equal(text[i], text[out + r]):
      i = i + 1
    elif less(text[i], text[out + r]):
      i, p = i + 1, i + 1 - out
    else:
      out, i, p = i - r, i - r + 1, 1
  return out, p
