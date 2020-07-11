def fill_one(word_1, word_2, n_2, R1, R2, r, s):
  j, i = 1, s
  R2[0] = n_2 + 1

  while i > 0:
    lower_b = 0 if j > r else R1[j]

    pos_b = R2[j - 1] - 1
    while pos_b > lower_b and word_1[i - 1] != word_2[pos_b - 1]:
      pos_b = pos_b - 1

    temp = max(pos_b, lower_b)
    if temp == 0:
      break

    R2[j] = temp
    i, j = i - 1, j + 1

  return j - 1


def cal_mid(word_1, word_2, n_1, n_2, x):
  r = 0
  LL, R1, R2 = [0] * (n_2 + 1), [0] * (n_2 + 1), [0] * (n_2 + 1)

  for s in range(n_1, n_1 - x - 1, -1):
    r = fill_one(word_1, word_2, n_2, R1, R2, r, s)
    R1[:r + 1] = R2[:r + 1]

  LL[:r + 1] = R1[:r + 1]

  return LL, r


def solve_base_case(word_1, word_2, n_1, n_2, p):
  lcs = ''
  LL, _ = cal_mid(word_1, word_2, n_1, n_2, n_1 - p)

  i = 1
  while i <= p and word_1[i - 1] == word_2[LL[p - i + 1] - 1]:
    lcs += word_1[i - 1]
    i = i + 1

  i = i + 1
  while i <= n_1:
    lcs += word_1[i - 1]
    i = i + 1

  return lcs


def find_perfect_cut(word_1, word_2, n_1, n_2, p, w):
  rev_w1, rev_w2 = word_1[::-1], word_2[::-1]
  LL1, r_1 = cal_mid(rev_w1, rev_w2, n_1, n_2, w)

  for j in range(0, r_1 + 1):
    LL1[j] = n_2 + 1 - LL1[j]

  LL2, r_2 = cal_mid(word_1, word_2, n_1, n_2, w)

  k = 0
  for i in range(0, r_1 + 1):
    if p - i <= r_2 and LL1[i] < LL2[p - i]:
      k = i

  return k + w, LL1[k]


def longest_common_subsequence(word_1, word_2, n_1, n_2, p):
  w = (n_1 - p) // 2
  w_prim = (n_1 - p + 1) // 2
  if n_1 - p < 2:
    c = solve_base_case(word_1, word_2, n_1, n_2, p)
  else:
    u, v = find_perfect_cut(word_1, word_2, n_1, n_2, p, w)
    c1 = longest_common_subsequence(word_1[:u], word_2[:v], u, v, u - w)
    c2 = longest_common_subsequence(word_1[u:], word_2[v:],
                                    n_1 - u, n_2 - v, n_1 - u - w_prim)
    c = c1 + c2
  return c


def find_lcs_length(word_1, word_2, n_1, n_2):
  r, s = 0, n_1 + 1
  R1, R2 = [0] * (n_2 + 1), [0] * (n_2 + 1)

  while s > r:
    s = s - 1
    r = fill_one(word_1, word_2, n_2, R1, R2, r, s)

    R1[:r + 1] = R2[:r + 1]

  return s

def distance(word_1, word_2, n_1, n_2, _):
  return n_1 + n_2 - 2 * find_lcs_length(word_1[1:], word_2[1:], n_1, n_2)

def linear_space_lcs(word_1, word_2, n_1, n_2, _):
  p = find_lcs_length(word_1[1:], word_2[1:], n_1, n_2)
  result = longest_common_subsequence(word_1[1:], word_2[1:], n_1, n_2, p)
  return result, n_1 + n_2 - 2 * p
