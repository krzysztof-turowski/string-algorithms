
from compression import lpf


def naive(w, n):
  LZ = []
  i = 1
  while i <= n:
    matched = [w[i:(i + k)]
           for k in range(1, n) if w.index(w[i:(i + k)]) < i]
    longest = (matched or [w[i]])[-1]
    LZ += [len(longest)]
    i += len(longest)

  return [-1] + LZ

def chrochemore_ille_smith(w, n):
  LZ = []
  LPF = lpf.chrochemore_ille_smith(w, n)

  pos = 1
  while pos <= n:
    LZ += [max(1, LPF[pos])]
    pos += LZ[-1]

  return [-1] + LZ
