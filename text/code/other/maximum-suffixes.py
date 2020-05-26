def maximum_suffixes(w, m):
  w_rev = w[0] + w[-1:0:-1]
  PREF = prefix.prefix_prefix(w_rev, m)
  S = [PREF[0]] + PREF[-1:0:-1]
  return S