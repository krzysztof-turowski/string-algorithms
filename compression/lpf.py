
from string_indexing import lcp, suffix_array


def naive(w, n):
  ret = []
  for i in range(1, n + 1):
    right = w[i:]
    while True:
      if right in w[1:(i + len(right) - 1)]:
        ret += [len(right)]
        break
      right = right[:-1]
  return [-1] + ret


def chrochemore_ille_smith(text, n, SA=None, LCP=None):
  SA = SA or suffix_array.small_large(text, n)
  LCP = LCP or lcp.kasai(SA, text, n)
  return compute_cis_lpf(n, SA, LCP)


def compute_cis_lpf(n, SA, LCP):
  SA += [-1]
  LCP += [0]
  LPF = [-1] * (n + 1)

  L = [1]

  for i in range(2, n + 2):
    while (L and
         ((SA[i] < SA[L[-1]]) or
        ((SA[i] > SA[L[-1]]) and LCP[i] <= LCP[L[-1]]))):
      if SA[i] < SA[L[-1]]:
        LPF[SA[L[-1]]] = max(LCP[L[-1]], LCP[i])
        LCP[i] = min(LCP[L[-1]], LCP[i])
      else:
        LPF[SA[L[-1]]] = LCP[L[-1]]
      L.pop()
    L.append(i)

  return LPF


def chrochemore_ille_smith_no_stack(text, n, SA=None, LCP=None):
  SA = SA or suffix_array.small_large(text, n)
  LCP = LCP or lcp.from_suffix_array(SA, text, n)
  return compute_cis_lpf_no_stack(n, SA, LCP)


def compute_cis_lpf_no_stack(n, SA, LCP):
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

  def rec(i, t):
    return update(i, t) or rec(rec(i + 1, i), t)

  c = 1
  while c <= n:
    c = rec(c + 1, c)

  return LPF
