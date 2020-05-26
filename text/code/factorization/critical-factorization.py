def critical_factorization(text, n):
  index_lt, p_lt = maximum_suffix(text, n)
  index_gt, p_gt = maximum_suffix(
      text, n, less = operator.__gt__)
  return (index_lt, p_lt) if index_lt >= index_gt else (index_gt, p_gt)
