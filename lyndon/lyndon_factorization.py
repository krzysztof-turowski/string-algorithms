import operator

def duval(text, n, less = operator.__lt__):
  i = 1
  while i <= n:
    j, k = i + 1, i
    while j <= n and not less(text[j], text[k]):
      if less(text[k], text[j]):
        k = i
      else:
        k += 1
      j += 1
    while i <= k:
      yield (i, i + j - k)
      i += j - k
  