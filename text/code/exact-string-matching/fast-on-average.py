def fast_on_average(t, w, n, m):
  S = build_suffix_tree(w)
  i, r = m, 2 * math.ceil(math.log(m, 2))
  while i <= n:
    if S.contains(t[(i - r):(i + 1)]):
      subt = t[0] + t[(i - m + 1):min(i - r + m - 1, n + 1)]
      subn = min(i - r + m - 1, n + 1) - (i - m + 1)
      for out in knuth_morris_pratt(subt, w, subn, m)
        yield out
    i = i + m - r
