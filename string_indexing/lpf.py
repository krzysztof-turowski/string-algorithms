from string_indexing import lcp, suffix_array


def naive(w, n):
  ret = []
  for i in range(1, n + 1):
    right = w[i:]
    while True:
      if right in w[1:(i + len(right) - 1)]:
        ret.append(len(right))
        break
      right = right[:-1]
  return [-1] + ret


def crochemore_ilie_smyth(text, n, SA=None, LCP=None):
  SA = SA or suffix_array.small_large(text, n)
  LCP = LCP or lcp.kasai(SA, text, n)
  return _compute_cis_lpf(SA, LCP, n)


def _compute_cis_lpf(SA, LCP, n):
  SA += [-1]
  LCP += [0]
  LPF = [-1] * (n + 1)

  L = [1]

  for i in range(2, n + 2):
    while L:
      if SA[i] < SA[L[-1]]:
        LPF[SA[L[-1]]] = max(LCP[L[-1]], LCP[i])
        LCP[i] = min(LCP[L[-1]], LCP[i])
      elif SA[i] > SA[L[-1]] and LCP[i] <= LCP[L[-1]]:
        LPF[SA[L[-1]]] = LCP[L[-1]]
      else:
        break
      L.pop()
    L.append(i)

  return LPF


def crochemore_ilie_smyth_no_stack(text, n, SA=None, LCP=None):
  SA = SA or suffix_array.small_large(text, n)
  LCP = LCP or lcp.from_suffix_array(SA, text, n)
  return _compute_cis_lpf_no_stack(SA, LCP, n)


def _compute_cis_lpf_no_stack(SA, LCP, n):
  SA += [-1]
  LCP += [0]
  LPF = [-1] * (n + 1)

  def update(i, t):
    if SA[i] < SA[t]:
      LPF[SA[t]] = max(LCP[t], LCP[i])
      LCP[i] = min(LCP[t], LCP[i])
      return i
    if SA[i] > SA[t] and LCP[i] <= LCP[t]:
      LPF[SA[t]] = LCP[t]
      return i
    return None

  def recurse(i, t):
    return update(i, t) or recurse(recurse(i + 1, i), t)

  c = 1
  while c <= n:
    c = recurse(c + 1, c)

  return LPF
