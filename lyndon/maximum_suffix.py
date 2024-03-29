import operator

from common import prefix

def naive(text, n):
  out = 1
  for i in range(2, n + 1):
    if text[out:] < text[i:]:
      out = i
  return out, prefix.period(text[0] + text[out:], n + 1 - out)

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

def from_suffix_array(SA, t, n):
  index = SA[-1]
  return index, prefix.period('#' + t[index:], n - index + 1)

def adamczyk_rytter(text, n, less = operator.__lt__):
  def equal(a, b):
    return not less(a, b) and not less(b, a)
  i, j = 1, 2
  while j <= n:
    k = 0
    while j + k < n and equal(text[i + k], text[j + k]):
      k += 1
    if less(text[i + k], text[j + k]):
      i += k + 1
    else:
      j += k + 1
    if i == j:
      j += 1
  return i, prefix.period("#" + text[i:], n + 1 - i)
