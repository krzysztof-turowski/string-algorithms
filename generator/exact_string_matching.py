import random
import re
import string
import scipy.stats

def uniform_generator(n, m, *, A = string.ascii_lowercase):
  while True:
    t = ''.join(random.choice(A) for i in range(n))
    w = ''.join(random.choice(A) for i in range(m))
    yield t, w

def geometric_generator(n, m, *, A = string.ascii_lowercase, p = 0.5):
  choice = [
    v for i, v in enumerate(A)
    for _ in range(int(1000 * scipy.stats.geom.pmf(i + 1, p)))]
  while True:
    t = ''.join(random.choice(choice) for i in range(n))
    w = ''.join(random.choice(choice) for i in range(m))
    yield t, w

def natural_generator(n, m, filename):
  RE_WHITESPACE = re.compile(r'\s+')
  with open(filename, 'r', encoding = 'UTF-8') as file:
    data = ''.join(e for e in RE_WHITESPACE.sub(
      ' ', file.read().lower()).strip() if e.isalnum() or e == ' ')
  while True:
    t_index = random.randint(0, len(data) - n - 1)
    t = data[t_index:t_index + n + 1]
    w_index = random.randint(0, len(t) - m - 1)
    w = t[w_index:w_index + m]
    yield t, w

def bf_algorithm_hard_case(n):
  return 'a' * n + 'b', 'a' * (n // 2) + 'b'

def bm_algorithm_hard_case(n, m):
  return 'a' * n, 'a' * m

def ag_algorithm_hard_case(n, m):
  x, e = (m - 2) // 2, n // m
  w = 'a' * (x - 1) + 'b' + 'a' * x + 'b'
  return w * e, w
