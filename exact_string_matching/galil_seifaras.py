GS_K = 4


def perfect_factorization(w: str, m: int):
  p, q = 0, 0
  s, p1, q1 = 0, 1, 0,
  p2, q2 = 0, 0

  def new_p2():
    pass

  def new_p1():
    while True:
      while s + p1 + q1 + 1 < m and w[s + p1 + q1 + 1] == w[s + q1 + 1]:
        q1 += 1
      if p1 + q1 >= GS_K * p1:
        p2, q2 = q1, 0
        new_p2()
      elif s + p1 + q1 < m:
        p1 += q1 // GS_K + 1
        q1 = 0
      else:
        break
