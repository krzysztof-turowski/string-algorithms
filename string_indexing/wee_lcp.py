import numpy as np

def compute_inversed_suffix_array(suf_array):
  inv_suf_array = [0] * len(suf_array)
  for i, suf_i in enumerate(suf_array):
    if i > 0:
      inv_suf_array[suf_i] = i
  return inv_suf_array

def compute_seqence_diff(inv_suf_array, lcp_array):
  diff = [0] * len(inv_suf_array)
  for i, inv_suf_i in enumerate(inv_suf_array):
    if i > 0:
      diff[i] = lcp_array[inv_suf_i] + i
  return diff

def compute_bit_string(diff):
  bit_stirng = ""
  for i, diff_i in enumerate(diff):
    if i > 0:
      zeros = diff[i] - diff[i-1]
      if i == 1:
        zeros = diff_i
      bit_stirng += '0' * zeros
      bit_stirng += '1'
  return bit_stirng

def compress_lcp_to_bit_string(lcp_array, suf_array):
  inv_suf_array = compute_inversed_suffix_array(suf_array)
  diff = compute_seqence_diff(inv_suf_array, lcp_array)
  return compute_bit_string(diff)

def brutal_select_one(bit_string, i):
  # Structure for this select for bit string was not described in this paper
  # For simplicity we use naive one
  # Used as substitute in 2n version
  # Used only while compressing for o(n) version
  st = i
  if i == 0:
    return 0
  for idx, bit_string_i in enumerate(bit_string):
    if bit_string_i == '1':
      i -= 1
      if i == 0:
        return idx+1 # +1 since we index from 0
  print(bit_string)
  print(st)
  raise Exception("Not enough 1s in bit-string")

def hardcode_interval(bit_string, begin, end):
  # begin and end are inclusive
  hardcoded = []
  for i in range(begin, end + 1):
    hardcoded.append(brutal_select_one(bit_string, i))
  return hardcoded

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

    self.text = text
    self.suf_array = suf_array

    self.kappa = int(np.log2(len(text))**2)
    self.lambd = int(np.log2(self.kappa )**2)
    self.limit = int(np.log2(len(text))**delta)

    self.net = [0 for _ in range(int((len(text) - 1) / self.kappa) + 2)]
    self.hel = [0 for _ in range(int((len(text) - 1) / self.kappa) + 2)]

    self.compress_bit_string(bit_string)

  def compress_bit_string(self, bit_string):
    for i in range(1, len(self.net)):
      if self.kappa * i > len(self.text): # last interval
        self.net[i] = brutal_select_one(bit_string, len(self.text))
        self.hel[i] = hardcode_interval(bit_string,
                                           self.kappa * (i - 1) + 1,
                                           len(self.text)) # inclusive
      else:
        self.net[i] = brutal_select_one(bit_string, self.kappa * i)
        interval_size = self.net[i] - self.net[i - 1]
        if interval_size > self.kappa**2:
          self.hel[i] = hardcode_interval(bit_string,
                                             self.kappa * (i - 1) + 1,
                                             self.kappa) # inclusive
        else:
          interval = bit_string[self.net[i - 1] : self.net[i]]
          self.hel[i] = self.compress_interval(interval)

  def compress_interval(self, I):
    N_prime_size = int((self.kappa - 1) / self.lambd) + 2
    N_prime = [0 for _ in range(N_prime_size)]
    H_prime = [0 for _ in range(N_prime_size)]
    for i in range(1, len(N_prime)):
      if self.lambd * i > self.kappa:
        N_prime[i] = brutal_select_one(I, self.kappa) # last interval
        H_prime[i] = hardcode_interval(I, self.lambd * (i - 1) + 1,
                                            self.kappa) # inclusive
      else:
        N_prime[i] = brutal_select_one(I, self.lambd * i) # last interval
        mini_interval_size = N_prime[i] - N_prime[i - 1]
        if mini_interval_size > self.limit:
          H_prime[i] = hardcode_interval(I, self.lambd * (i - 1) + 1,
                                              self.lambd * i) # inclusive
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
    if i == 0:
      return -1
    if i < 2:
      return 0
    approx = max(0, self.select_one(self.suf_array[i]) - 2 * self.suf_array[i])
    idx_i = self.suf_array[i] + approx
    idx_j = self.suf_array[i - 1] + approx
    text = self.text + '$'
    while text[idx_i] == text[idx_j]:
      approx += 1
      idx_i += 1
      idx_j += 1
    return approx
