import numpy

def compute_inversed_suffix_array(suf_array):
  inv_suf_array = [0] * len(suf_array)
  for i, s in enumerate(suf_array[1:], start = 1):
    inv_suf_array[s] = i
  return inv_suf_array

def compute_seqence_diff(inv_suf_array, lcp_array):
  return [0] + [
        lcp_array[v] + i for i, v in enumerate(inv_suf_array[1:], start = 1)]

def compute_bit_string(diff):
  return '1'.join('0' * (i - j) for i, j in zip(diff[1:], diff)) + '1'

def compress_lcp_to_bit_string(lcp_array, suf_array):
  inv_suf_array = compute_inversed_suffix_array(suf_array)
  return compute_bit_string(compute_seqence_diff(inv_suf_array, lcp_array))

def brutal_select_one(bit_string, i):
  # Structure for this select for bit string was not described in this paper
  # For simplicity we use naive one
  # Used as substitute in 2n version
  # Used only while compressing for o(n) version
  index = 0
  for _ in range(i):
    index = bit_string.find('1', index) + 1
  return index

def hardcode_interval(bit_string, begin, end):
  return [brutal_select_one(bit_string, i) for i in range(begin, end)]

class CompressedLCP2n:
  def __init__(self, bit_string, suf_array):
    self.suf_array = suf_array
    self.bit_string = bit_string

  def lcp(self, i):
    if i == 0:
      return -1
    result = brutal_select_one(self.bit_string, self.suf_array[i])
    return result - 2 * self.suf_array[i]

  def get_lcp_array(self):
    return [self.lcp(i) for i in range(1, len(self.suf_array))]

class CompressedLCPon:
  def __init__(self, bit_string, text, suf_array, delta):
    self.text, self.suf_array = text, suf_array

    self.kappa = int(numpy.log2(len(text)) ** 2)
    self.lambd = int(numpy.log2(self.kappa) ** 2)
    self.limit = int(numpy.log2(len(text)) ** delta)

    self.net = [0] * (int((len(text) - 1) / self.kappa) + 2)
    self.hel = [0] * (int((len(text) - 1) / self.kappa) + 2)

    self.compress_bit_string(bit_string)

  def compress_bit_string(self, bit_string):
    for i in range(1, len(self.net)):
      if self.kappa * i > len(self.text): # last interval
        self.net[i] = brutal_select_one(bit_string, len(self.text))
        self.hel[i] = hardcode_interval(
            bit_string, self.kappa * (i - 1) + 1, len(self.text) + 1)
      else:
        self.net[i] = brutal_select_one(bit_string, self.kappa * i)
        interval_size = self.net[i] - self.net[i - 1]
        if interval_size > self.kappa ** 2:
          self.hel[i] = hardcode_interval(
              bit_string, self.kappa * (i - 1) + 1, self.kappa + 1)
        else:
          interval = bit_string[self.net[i - 1] : self.net[i]]
          self.hel[i] = self.compress_interval(interval)

  def compress_interval(self, I):
    N_prime_size = int((self.kappa - 1) / self.lambd) + 2
    N_prime, H_prime = [0] * N_prime_size, [0] * N_prime_size
    for i in range(1, len(N_prime)):
      if self.lambd * i > self.kappa:
        N_prime[i] = brutal_select_one(I, self.kappa) # last interval
        H_prime[i] = hardcode_interval(
            I, self.lambd * (i - 1) + 1, self.kappa + 1)
      else:
        N_prime[i] = brutal_select_one(I, self.lambd * i) # last interval
        mini_interval_size = N_prime[i] - N_prime[i - 1]
        if mini_interval_size > self.limit:
          H_prime[i] = hardcode_interval(
              I, self.lambd * (i - 1) + 1, self.lambd * i + 1)
        else:
          pass # this case needs iteration through text
    return (N_prime, H_prime)

  def select_one(self, i):
    interval_number = int((i - 1) / self.kappa) + 1
    if self.kappa * interval_number > len(self.text):
      idx = (i - 1) - (interval_number - 1) * self.kappa
      return self.hel[interval_number][idx]
    interval_size = self.net[interval_number] - self.net[interval_number - 1]
    if interval_size > self.kappa**2:
      idx = i - (interval_number - 1) * self.kappa
      return self.hel[interval_number][idx] # hardcoded
    mini_interval_number = int(((i-1) % self.kappa) / self.lambd) + 1
    mini_interval_start = self.hel[interval_number][0][mini_interval_number - 1]
    mini_interval_finish = self.hel[interval_number][0][mini_interval_number]
    mini_interval_size = mini_interval_finish - mini_interval_start
    if mini_interval_size > self.limit:
      a = self.net[interval_number - 1]
      idx = ((i - 1) % self.kappa) % self.lambd
      b = self.hel[interval_number][1][mini_interval_number][idx]
      return a + b # hardcoded
    a = self.net[interval_number - 1]
    b = self.hel[interval_number][0][mini_interval_number - 1]
    return a + b # linear check will be performed

  def lcp(self, i):
    if i < 2:
      return i - 1
    approx = max(0, self.select_one(self.suf_array[i]) - 2 * self.suf_array[i])
    idx_i, idx_j = self.suf_array[i] + approx, self.suf_array[i - 1] + approx
    text = self.text + '$'
    while text[idx_i] == text[idx_j]:
      approx, idx_i, idx_j = approx + 1, idx_i + 1, idx_j + 1
    return approx
