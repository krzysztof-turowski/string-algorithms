from common.prefix import get_longest_common_prefix

def lcplr_from_lcp(lcp, n):
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


def get_word_to_edge_lcp(l, r):
  return l if l >= r else r


def get_edge_to_mid_lcp(l, r, lcplr, left, mid, right):
  return lcplr[(left, mid)] if l >= r else lcplr[(mid, right)]


def get_word_to_mid_lcp(SA, text, word, mid, word_to_edge_lcp, edge_to_mid_lcp):
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


def right_bound_with_lcplr(SA, lcplr, text, word, n, m):
  l, r = initialize_lr(SA, text, word, n)

  if r == m or word[r + 1:] > text[SA[n] + r:]:
    return n + 1

  left, right = 1, n
  while left + 1 < right:
    mid = (left + right) // 2
    word_to_edge_lcp = get_word_to_edge_lcp(l, r)
    edge_to_mid_lcp = get_edge_to_mid_lcp(l, r, lcplr, left, mid, right)
    word_to_mid_lcp = get_word_to_mid_lcp(SA, text, word, mid,
                                          word_to_edge_lcp, edge_to_mid_lcp)

    if word_to_mid_lcp == m or \
       word[1 + word_to_mid_lcp] > text[SA[mid] + word_to_mid_lcp]:
      left, l = mid, word_to_mid_lcp
    else:
      right, r = mid, word_to_mid_lcp
  return right


def left_bound_with_lcplr(SA, lcplr, text, word, n, m):
  l, r = initialize_lr(SA, text, word, n)

  if l == m or word[l + 1:] <= text[SA[0] + l:]:
    return 1
  if r < m and word[r + 1:] > text[SA[n] + r:]:
    return n + 1

  left, right = 1, n
  while left + 1 < right:
    mid = (left + right) // 2
    word_to_edge_lcp = get_word_to_edge_lcp(l, r)
    edge_to_mid_lcp = get_edge_to_mid_lcp(l, r, lcplr, left, mid, right)
    word_to_mid_lcp = get_word_to_mid_lcp(SA, text, word, mid,
                                          word_to_edge_lcp, edge_to_mid_lcp)

    if word_to_mid_lcp == m or \
       word[1 + word_to_mid_lcp] <= text[SA[mid] + word_to_mid_lcp]:
      right, r = mid, word_to_mid_lcp
    else:
      left, l = mid, word_to_mid_lcp

  return right


def contains_with_lcplr(SA, lcplr, text, word, n, m):
  text += "$"
  low = left_bound_with_lcplr(SA, lcplr, text, word, n, m)
  high = right_bound_with_lcplr(SA, lcplr, text, word, n, m)
  yield from sorted([SA[i] for i in range(low, high)])
