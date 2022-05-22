from dataclasses import dataclass
from typing import Optional

GS_K = 4

@dataclass
class Hrp:
  period: int
  len: int

def preprocess_first_two_hrps(w: str, m: int):
  pos = 1
  j = 0
  hrp1: Optional[Hrp] = None
  while pos + j < m:
    while pos + j + 1 < m and w[j + 1] == w[pos + j + 1]:
      j += 1
    prefix_len = pos + j

    if pos * GS_K <= prefix_len:
      next_hrp = Hrp(period=pos, len=prefix_len)
      if hrp1 is not None:
        return hrp1, next_hrp
      hrp1 = next_hrp

    if hrp1 is not None and hrp1.period * 2 <= j <= hrp1.len:
      pos = pos + hrp1.period
      j = j - hrp1.period
    else:
      pos += (j // GS_K) + 1
      j = 0

  return hrp1, None


def perfect_factorization(w: str, m: int):
  j = 0
  hrp1, hrp2 = preprocess_first_two_hrps(w, m)

  while hrp1 is not None and hrp2 is not None:
    j += hrp1.period
    hrp1, next_hrp2 = preprocess_first_two_hrps(w[j:], m - j)
    if hrp1 is not None and hrp1.period >= hrp2.period:
      hrp2 = next_hrp2

  return w[:j+1], w[j:], j, m - j, hrp1


def simple_text_search(t: str, v: str, n: int, m: int, hrp1: Optional[Hrp]):
  pos, j = 0, 0
  while pos + m <= n:
    while j < m and v[j+1] == t[pos + j + 1]:
      j += 1

    if j == m:
      yield pos + 1

    if hrp1 is not None and 2 * hrp1.period <= j <= hrp1.len:
      pos = pos + hrp1.period
      j = j - hrp1.period
    else:
      pos += (j // GS_K) + 1
      j = 0

def galil_seifaras(t: str, w: str, n: int, m: int):
  u, v, uLen, vLen, hrp1 = perfect_factorization(w, m)
  for i in simple_text_search(t, v, n, vLen, hrp1):
    if i > uLen and u[1:] == t[i - uLen :i]:
      yield i - uLen

# if __name__ == "__main__":
#   # '#abaaabbaababb', '#abb', 13, 3, [5, 11]
#   print(list(galil_seifaras('#abaaabbaababb', '#abb', 13, 3)))
#   # Expect [5, 11]
