from common import prefix
from string_indexing import suffix_array

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
  R, k = suffix_array.get_reverse(SA), 0
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

def build_lcp_lr(LCP, n):
  """Builds LCP-LR dictionary from LCP array"""
  LCP_LR = {}
  def _build_lcp_lr(left, right):
    if left + 1 == right:
      common_prefix = LCP[right]
    else:
      mid = (left + right) // 2
      common_prefix = min(_build_lcp_lr(left, mid), _build_lcp_lr(mid, right))
    LCP_LR[(left, right)] = common_prefix
    return common_prefix
  _build_lcp_lr(1, n)
  return LCP_LR

def _get_word_to_mid_lcp(
    SA, text, word, mid, word_to_edge_lcp, edge_to_mid_lcp):
  """Finds longest common prefix between mid and word"""
  if edge_to_mid_lcp >= word_to_edge_lcp:
    word_to_mid_lcp = word_to_edge_lcp + prefix.get_longest_common_prefix(
        text[SA[mid] + word_to_edge_lcp:], word[1 + word_to_edge_lcp:])
  else:
    word_to_mid_lcp = edge_to_mid_lcp
  return word_to_mid_lcp

def _initialize_lr(SA, text, word, n):
  l = prefix.get_longest_common_prefix(text[SA[1]:], word[1:])
  r = prefix.get_longest_common_prefix(text[SA[n]:], word[1:])
  return l, r

def _find_bound_with_lcplr(SA, LCP_LR, text, word, n, m, lower_bound):
  """Finds lower or upper bound of occurences of word in SA"""
  l, r = _initialize_lr(SA, text, word, n)
  if lower_bound:
    if l == m or word[l + 1:] <= text[SA[1] + l:]:
      return 1
    if r < m and word[r + 1:] > text[SA[n] + r:]:
      return n + 1
  else:
    if l < m and word[l + 1:] <= text[SA[1] + l:]:
      return 1
    if r == m or word[r + 1:] > text[SA[n] + r:]:
      return n + 1

  left, right = 1, n
  while left + 1 < right:
    mid = (left + right) // 2
    word_to_edge_lcp = max(l, r)
    edge_to_mid_lcp = LCP_LR[(left, mid)] if l >= r else LCP_LR[(mid, right)]
    word_to_mid_lcp = _get_word_to_mid_lcp(
        SA, text, word, mid, word_to_edge_lcp, edge_to_mid_lcp)
    if word_to_mid_lcp == m:
      if lower_bound:
        right, r = mid, word_to_mid_lcp
      else:
        left, l = mid, word_to_mid_lcp
    elif word[1 + word_to_mid_lcp] <= text[SA[mid] + word_to_mid_lcp]:
      right, r = mid, word_to_mid_lcp
    else:
      left, l = mid, word_to_mid_lcp

  return right

def contains(SA, LCP_LR, text, word, n, m):
  """Finds occurences of word in text in O(m + log n) (Manber & Myers, 1993)"""
  text += "$"
  low = _find_bound_with_lcplr(
      SA, LCP_LR, text, word, n, m, lower_bound = True)
  high = _find_bound_with_lcplr(
      SA, LCP_LR, text, word, n, m, lower_bound = False)
  yield from sorted([SA[i] for i in range(low, high)])
