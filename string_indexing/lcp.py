import math
from common import prefix
from string_indexing import suffix_array, wee_lcp

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
  text += '$'
  low = _find_bound_with_lcplr(
      SA, LCP_LR, text, word, n, m, lower_bound = True)
  high = _find_bound_with_lcplr(
      SA, LCP_LR, text, word, n, m, lower_bound = False)
  yield from sorted([SA[i] for i in range(low, high)])

def build_plcp_a(SA, text, n, q = 1):
  """q is a compression factor
  Computes PLCP of size (n/q) using PHI array"""
  text += '$'
  PHI = _compute_phi(SA, n, q)
  return _compute_plcp_from_phi(PHI, text, q)

def build_plcp_b(SA, text, n, q = 1):
  """q is a compression factor
  Computes PLCP of size (n/q) using Irreducible LCP values"""
  text += '$'
  return _compute_plcp_from_irreducible_lcp_values(SA, text, n, q)

def _compute_phi(SA, n, q):
  """Computes array PHI[SA[i]] = SA[i - 1]"""
  PHI = [-1] + [0] * math.ceil(n / q)
  for SA_prev, SA_next in zip(SA, SA[1:]):
    if SA_next % q == 0:
      PHI[SA_next // q] = SA_prev
  return PHI

def _compute_plcp_from_phi(PHI, text, q):
  """Computes array PLCP[i] = lcp(i, PHI[i])"""
  PLCP = [0] * len(PHI)
  l = 0
  for i, phi in enumerate(PHI[1:], start = 1):
    l += prefix.get_longest_common_prefix(text[i * q + l:], text[phi + l:])
    PLCP[i] = l
    l = max(l - q, 0)
  return PLCP

def _compute_plcp_from_irreducible_lcp_values(SA, text, n, q):
  """Computes irreducible lcp values:
  PLCP[i] such that text[i - 1] != text[PHI[i] - 1],
  then fills in remaining values"""
  PLCP = [0] * (1 + math.ceil(n / q))
  for SA_prev, SA_next in zip(SA[1:], SA[2:]):
    if text[SA_prev - 1] != text[SA_next - 1]:
      l = prefix.get_longest_common_prefix(text[SA_prev:], text[SA_next:])
      k = math.ceil(SA_next / q)
      PLCP[k] = max(PLCP[k], l - k * q + SA_next)
  for i in range(1, len(PLCP) - 1):
    PLCP[i + 1] = max(PLCP[i + 1], PLCP[i] - q)
  return PLCP

def convert_plcp_to_lcp(PLCP, SA, text, q = 1):
  """Computes array LCP[i] = PLCP[SA[i]]"""
  text += '$'
  def _plcp(i, j):
    d, rem = j // q, j % q
    if rem == 0:
      return PLCP[d]
    l = max(PLCP[d] - rem, 0)
    r = PLCP[d + 1] + q - rem if d + 1 < len(PLCP) else q
    return next((k for k in range(l, r)
                 if text[SA[i] + k] != text[SA[i - 1] + k]), r)
  return [-1] + [_plcp(i, SA[i]) for i, sa in enumerate(SA[1:], start = 1)]

def from_wee_lcp_2n(text, n):
  SA = suffix_array.prefix_doubling(text, n)
  LCP = kasai(SA, text, n)
  bit_string = wee_lcp.compress_lcp_to_bit_string(LCP, SA)
  wee_lcp_2n = wee_lcp.CompressedLCP2n(bit_string, SA)
  return [wee_lcp_2n.lcp(i) for i in range(n + 1)]

def from_wee_lcp_o_n(text, n):
  SA = suffix_array.naive(text, len(text))
  LCP = kasai(SA, text, len(text))
  bit_string = wee_lcp.compress_lcp_to_bit_string(LCP, SA)
  wee_lcp_on = wee_lcp.CompressedLCPon(bit_string, text, SA, 0.5)
  return [-1] + [wee_lcp_on.lcp(i) for i in range(2, n + 2)]
