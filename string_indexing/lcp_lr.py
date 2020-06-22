from common.prefix import get_longest_common_prefix

def lcplr_from_lcp(lcp, n):
  """Builds LCP-LR dictionary from LCP array"""
  lcplr = {}
  def fill_lcplr(left, right):
    if right == left + 1:
      common_prefix = lcp[right]
    else:
      mid = (left + right) // 2
      common_prefix = min(fill_lcplr(left, mid), fill_lcplr(mid,right))
    lcplr[(left, right)] = common_prefix
    return common_prefix

  fill_lcplr(1, n)
  return lcplr


def get_word_to_mid_lcp(SA, text, word, mid, word_to_edge_lcp, edge_to_mid_lcp):
  """Finds longest common prefix between mid and word"""
  if edge_to_mid_lcp >= word_to_edge_lcp:
    word_to_mid_lcp = word_to_edge_lcp + \
      get_longest_common_prefix(text[SA[mid] + word_to_edge_lcp:],
                                word[1 + word_to_edge_lcp:])
  else:
    word_to_mid_lcp = edge_to_mid_lcp
  return word_to_mid_lcp


def initialize_lr(SA, text, word, n):
  l = get_longest_common_prefix(text[SA[1]:], word[1:])
  r = get_longest_common_prefix(text[SA[n]:], word[1:])
  return l, r


def find_bound_with_lcplr(SA, lcplr, text, word, n, m, lower_bound = True):
  """Finds lower or upper bound of occurences of word in SA"""
  l, r = initialize_lr(SA, text, word, n)

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
    edge_to_mid_lcp = lcplr[(left, mid)] if l >= r else lcplr[(mid, right)]
    word_to_mid_lcp = get_word_to_mid_lcp(SA, text, word, mid,
                                          word_to_edge_lcp, edge_to_mid_lcp)

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


def contains_with_lcplr(SA, lcplr, text, word, n, m):
  """Finds occurences of word in text in O(m + log n) (Manber & Myers, 1993)"""
  text += "$"
  low = find_bound_with_lcplr(SA, lcplr, text, word, n, m, lower_bound = True)
  high = find_bound_with_lcplr(SA, lcplr, text, word, n, m, lower_bound = False)
  yield from sorted([SA[i] for i in range(low, high)])
