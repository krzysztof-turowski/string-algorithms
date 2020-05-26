def reverse(SA):
  reverse = [0] * len(SA)
  for i in range(len(SA)):
    reverse[SA[i] - 1] = i + 1
  return reverse

def prefix_doubling(text, n):
  '''Computes suffix array using Karp-Miller-Rosenberg algorithm'''
  text += '$'
  mapping = {v: i + 1 for i, v in enumerate(sorted(set(text[1:])))}
  R, k = [mapping[v] for v in text[1:]], 1
  while k < 2 * n:
    pairs = [(R[i], R[i + k] if i + k < len(R) else 0) for i in range(len(R))]
    mapping = {v: i + 1 for i, v in enumerate(sorted(set(pairs)))}
    R, k = [mapping[pair] for pair in pairs], 2 * k
  return reverse(R)
