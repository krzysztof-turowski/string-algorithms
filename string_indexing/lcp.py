def from_suffix_array(SA, text, n):
  text += '$'
  return [-1] + [
      next(i for i, x, y in zip(range(n), text[i:], text[j:]) if x != y)
      for i, j in zip(SA, SA[1:])]

def from_suffix_tree(ST):
  def _get_lcp(v):
    if len(v.children) == 0:
      return []
    L = [lcp for _, child in sorted(v.children.items())
         for lcp in _get_lcp(child) + [v.depth]]
    return L[:-1]
  ST.set_depth()
  return [-1] + _get_lcp(ST)

def kasai(SA, text, n):
  text += '$'
  L = [-1] * (n + 1)
  R, k = _reverse(SA), 0
  for i in range(1, n + 2):
    if R[i - 1] != n + 1:
      j = SA[R[i - 1]]
      while i + k <= n and j + k <= n and text[i + k] == text[j + k]:
        k += 1
      L[R[i - 1]] = k
      k = max(k - 1, 0)
    else:
      k = 0
  return L
