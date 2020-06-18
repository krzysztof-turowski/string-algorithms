def boyer_moore_bad_environment(A, p, m, k):
  bad_table = {(i, a): True for i in range(1, m + 1) for a in A}
  for i in range(1, m + 1):
    for j in range(max(0, i - k), min(i + k, m) + 1):
      bad_table[(j, p[i])] = False
  return bad_table


def boyer_moore_multi_dim_shift(A, p, m, k):
  ready = {a: m + 1 for a in A}
  BM_k = {(i, a): m for a in A for i in range(m, m - k - 1, -1)}
  for i in range(m - 1, 0, -1):
    for j in range(ready[p[i]] - 1, max(i, m - k) - 1, -1):
      BM_k[(j, p[i])] = j - i
    ready[p[i]] = max(i, m - k)
  return BM_k


def boyer_moore_k_mismatches(text, p, n, m, k=0, A=None):
  if A is None:
    A = ['a', 'b', '?']

  BM_k = boyer_moore_multi_dim_shift(A, p, m, k)
  BAD = boyer_moore_bad_environment(A, p, m, k)

  j, top = m, min(k + 1, m)
  D_0 = list(range(m + 1))
  D_curr = D_0.copy()
  curr_col, j = next_possible_occurence(text, n, m, k, BM_k, BAD, j)

  last_col = curr_col + m + 2 * k - 1

  while curr_col <= n:
    for r in range(curr_col, last_col + 1):
      c = 0
      # evaluate another column of D
      for i in range(1, top + 1):
        if r <= n and p[i] == text[r]:
          d = c
        else:
          d = min(D_curr[i - 1], D_curr[i], c) + 1
        c = D_curr[i]
        D_curr[i] = d

      while D_curr[top] > k:
        top -= 1

      # if D[m] <= k we have a match
      if top == m:
        yield r
      else:
        top += 1

    next_possible, j = next_possible_occurence(text, n, m, k, BM_k, BAD, j)
    if next_possible > last_col + 1:
      D_curr, top, curr_col = D_0.copy(), min(k + 1, m), next_possible
    else:
      curr_col = last_col + 1

    last_col = next_possible + m + 2 * k


def next_possible_occurence(text, n, m, k, BM_k, BAD, j):
  while j <= n + k:
    r, i, bad, d = j, m, 0, m

    while i > k >= bad:
      if i >= m - k and r <= m:
        d = min(d, BM_k[(i, text[r])])

      if r <= m and BAD[(i, text[r])]:
        bad = bad + 1

      i, r = i - 1, r - 1

    if bad <= k:
      break

    j = j + max(k + 1, d)

  if j <= (n + k):
    npo = j - m - k
    j = j + max(k + 1, d)
    return npo, j

  return n + 1, j


def simple_dynamic(text, p, n, m, k=0):
  D = {(0, j): 0 for j in range(n + 1)}

  for i in range(m + 1):
    D[(i, 0)] = i

  for i in range(1, m + 1):
    for j in range(1, n + 1):
      D[(i, j)] = min(D[(i - 1, j)] + 1, D[(i, j - 1)] +
                      1, D[(i - 1, j - 1)] + int(p[i] != text[j]))

  for j in range(n + 1):
    if D[(m, j)] <= k:
      yield j


tex = '#aaabababbabaabbabababbababababbabababbabbbabababbabaaaaabbbababbbbba'
pat = '#a?a???b'
print(list(simple_dynamic(tex, pat, len(tex) - 1, len(pat) - 1, 4)))
print(list(boyer_moore_k_mismatches(tex, pat, len(tex) - 1,
                                    len(pat) - 1, 4)))
# '#abaaabbaababb', '#a?b', 13, 3, [4, 5, 8, 11]
