import math

def all_modular_inverses_list_for_prime(modulo):
  """
    returns list of length `modulo`, where
            (result[i]*i) % modulo == 1,  if i != 0, else
            result[0] = 0
  """
  assert is_prime(modulo), "modulo must be a prime number"

  modular_inverse = [0]*modulo
  modular_inverse[1] = 1
  for i in range(2, modulo):
    modular_inverse[i] = (modulo-(modulo//i)*modular_inverse[modulo%i])%modulo
  return modular_inverse

def is_prime(n):
  if n <= 1:
    return False
  i = 2
  while i*i <= n:
    if n%i == 0:
      return False
    i += 1
  return True

def smallest_prime_greater_or_equal_than(n):
  while not is_prime(n): # after O(ln n) steps we'll find a prime
    n += 1
  return n

def q_ary_entropy(x, q):
  """
  q-ary entropy from Gilbert-Varshamov bound
  https://en.wikipedia.org/wiki/Gilbert%E2%80%93Varshamov_bound_for_linear_codes
  """
  if x in [0,1]:
    return 0
  return x*math.log((q-1)/x)/math.log(q) + (1-x)*math.log(1/(1-x)/math.log(q))

def to_radix(value, base, width = None):
  """
  Base representation of value in `width` digits.
  Most significant digit first.
  """
  if width is None:
    width = max(math.ceil(math.log(value + 1, base)), 1)
  digits = [0] * width
  for i in range(width - 1, -1, -1):
    value, digits[i] = divmod(value, base)
  if value != 0:
    raise ValueError('value does not fit into the field')
  return digits

def from_radix(digits, base):
  """
  Inverse of to_radix.
  Most significant digit first.
  """
  value = 0
  for d in digits:
    value = value * base + d
  return value
