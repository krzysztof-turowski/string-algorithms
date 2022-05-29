import itertools
import numpy
from scipy.signal import convolve
from scipy.stats import binom
from approximate_string_matching import distance
from common import numeric
TOO_MANY_MISMATCHES = 'too many'

def apply_preprocessing(func):
  def wrapper(text, word, n, m, k, *args, **kwargs):
    if m > n:
      yield from ()
    else:
      # map characters to numbers, such that don't care is 0
      alphabet = set(list(text[1:] + word[1:])) - set('?')
      letter_mapping = {c: i for i, c in enumerate(alphabet, start = 1)}
      letter_mapping.update({'?': 0})

      # Since signal.convolve requires 0-indexing and we'll be working
      # only on numbers from now, we'll remove sharps so
      # text_numeric and word_numeric will be 0-indexed
      text_numeric = numpy.array([letter_mapping.get(c) for c in text[1:]])
      word_numeric = numpy.array([letter_mapping.get(c) for c in word[1:]])
      yield from map(
        lambda x: x+1,
        func(text_numeric, word_numeric, n, m, k, *args, **kwargs)
      )

  return wrapper

@apply_preprocessing
def nonrecursive_randomised(text_numeric, word_numeric, n, m, k):
  # constant for inner algorithm loop
  # selected empirically with 2x safety threshold,
  # which means, that K_CONST=15 also passes unit tests
  K_CONST = 30
  sample_rate = 1/max(k,1)

  def random_masked_word_generator():
    # O(k * log(n)) iterations
    for _ in range(int(k*(K_CONST+numpy.log(n)))):
      yield numpy.array(
        [x if numpy.random.random() < sample_rate else 0 for x in word_numeric]
      )

  return __nonrecursive_algorithm(
    text_numeric, word_numeric, n, m, k, random_masked_word_generator)

@apply_preprocessing
def nonrecursive_deterministic(text_numeric, word_numeric, n, m, k):
  ssf = generate_strongly_selective_family(m,k)

  def ssf_masked_word_generator():
    for s in ssf:
      yield numpy.array(
        [x if i in s else 0 for i,x in enumerate(word_numeric)]
      )

  return __nonrecursive_algorithm(
    text_numeric, word_numeric, n, m, k, ssf_masked_word_generator)

def __nonrecursive_algorithm(
  text_numeric, word_numeric, n, m, k, masked_word_generator):

  mismatches = [set() for _ in range(n-m+1)]
  for masked_word in masked_word_generator():
    found_mismatches = one_hamming_mismatch(text_numeric, masked_word)
    for i, x in enumerate(found_mismatches):
      if x is not None and x != TOO_MANY_MISMATCHES and len(mismatches[i]) < k:
        mismatches[i].add(x)

  yield from __checking_stage(text_numeric, word_numeric, mismatches)

@apply_preprocessing
def recursive(text_numeric, word_numeric, n, m, k):
  # constant for inner algorithm loop
  # selected empirically with 2x safety threshold,
  # which means, that KS_CONST=20 also passes unit tests
  KS_CONST = 40

  mismatches = [set() for _ in range(n-m+1)]
  E = [set() for _ in range(m)]

  ks = k
  while ks >= 1:
    sample_rate = 1/ks
    # O(ks + log(n)) iterations
    for _ in range(int(KS_CONST*ks + numpy.log(n))):
      masked_word = numpy.array(
        [x if numpy.random.random() < sample_rate else 0 for x in word_numeric]
      )
      found_mismatches = one_hamming_mismatch(
        text_numeric, masked_word, corrections=E
      )

      for i, x in enumerate(found_mismatches):
        if x is not None and x != TOO_MANY_MISMATCHES:
          if len(mismatches[i]) < k:
            E[x-i].add(i)
            mismatches[i].add(x)

      ks /= 2

  yield from __checking_stage(text_numeric, word_numeric, mismatches)


def __checking_stage(text_numeric, word_numeric, mismatches):
  clifford_array = __get_clifford_array(text_numeric, word_numeric, False)
  number_of_mismatches = [
    len(x) if __are_all_mismatches_found_at(
      i, x, text_numeric, word_numeric, clifford_array
    ) else TOO_MANY_MISMATCHES
    for i,x in enumerate(mismatches)
  ]
  return [
    i for i,x in enumerate(number_of_mismatches) if x != TOO_MANY_MISMATCHES
  ]

def one_hamming_mismatch(text_numeric, word_numeric, corrections=tuple()):
  """
  returns array of size (n-m+1), where i-th entry is either:
          * None, if text[i:i+m] and word matches exactly,
            ignoring already known mismatches from `corrections`
          * j, if there is exactly one not known yet mismach between
            text[i:i+m] and word, at position text[j] (and word[j-i]]
          * `TOO_MANY_MISMATCHES`, if there are more than 2 mismatches
            not know yet between text[i:i+m] and word
  """
  a0 = __get_clifford_array(text_numeric, word_numeric, False)
  a1 = __get_clifford_array(text_numeric, word_numeric, True)

  for j, corrections_at_j in enumerate(corrections):
    if word_numeric[j] != 0:
      for i in corrections_at_j:
        tv = text_numeric[i+j]
        wv = word_numeric[j]
        a0[i] -= tv*wv*(tv-wv)
        a1[i] -=  i*tv*wv*(tv-wv)

  possible_mismatch_position_in_text = [
    None if x0 == 0 else x1//x0 for x0,x1 in zip(a0,a1)
  ]
  mismatch_position = [
    x if __are_all_mismatches_found_at(
      i, [x], text_numeric, word_numeric, a0
    ) else TOO_MANY_MISMATCHES
    for i,x in enumerate(possible_mismatch_position_in_text)
  ]
  return mismatch_position

def __get_clifford_array(text_numeric, word_numeric, positional=False):
  r"""
  returns \Sum_{j=1^m} p_j*t_{i+j-1}*(p_j - t_{i+j-1})^2 if positional == False
          otherwise \Sum_{j=1^m} (i+j-1)*p_j*t_{i+j-1}*(p_j - t_{i+j-1})^2.
          Note a slight difference between paper and code -
          we use plain p,t outside the square, instead of clipped p',t',
          so the result will be scaled by these factors
  """
  indices = numpy.ones(
    len(text_numeric)) if not positional else numpy.arange(len(text_numeric))

  first_component = convolve(
    (word_numeric**3)[::-1], indices*text_numeric, mode='valid', method='fft')
  second_component = convolve(
    (word_numeric**2)[::-1],
    indices*text_numeric**2,
    mode='valid', method='fft')
  third_component = convolve(
    (word_numeric)[::-1], indices*text_numeric**3, mode='valid', method='fft')

  return numpy.rint(
    first_component - 2*second_component + third_component).astype(int)

def __are_all_mismatches_found_at(
  i, mismatch_positions_in_text, text_numeric, word_numeric, clifford_array):

  correlation_correction = 0
  for mismatch_pos in mismatch_positions_in_text:
    if mismatch_pos is not None and \
       mismatch_pos < len(text_numeric) and \
       mismatch_pos-i < len(word_numeric):

      tv = text_numeric[mismatch_pos]
      wv = word_numeric[mismatch_pos-i]
      correlation_correction += tv*wv*(tv-wv)**2

  return correlation_correction == clifford_array[i]


def naive_hamming_with_mismatches(t, w, n, m, k):
  for i in range(1, n - m + 2):
    if distance.hamming_distance('#' + t[i:i + m], w, m, m, '?') <= k:
      yield i


# Strongly selective families
# https://doi.org/10.48550/arXiv.0712.3876

def generate_strongly_selective_family(n, r):
  if r == 0:
    return [[]]

  if n == 1 or r*r*numpy.log(n) >= n:
    return [{i} for i in range(n)]

  delta = (r-1)/r
  q = numeric.smallest_prime_greater_or_equal_than(2*r)

  k = int(numpy.ceil(numpy.log(n) / numpy.log(q)))
  m = int(numpy.ceil(k/(1-numeric.q_ary_entropy(delta,q))))
  matrix = linear_code_matrix_with_high_rate(m, k, delta, q)
  S = {(i,l): set() for i in range(m) for l in range(q)}

  for i,y in enumerate(itertools.product(range(q), repeat=k)):
    z = (matrix@y)%q
    for p in range(m):
      if i < n:
        S[(p, z[p])].add(i)

  return list(x for x in S.values() if len(x) > 0)

def linear_code_matrix_with_high_rate(m, k, delta, q):
  G = numpy.zeros((m,k), dtype=int)
  modular_inverse = numeric.all_modular_inverses_list_for_prime(q)
  number_of_non_zeroes_in_Gy = {
    tuple(x_r)+(x,):0
    for x in range(1,q)
    for j in range(k)
    for x_r in itertools.product(range(q), repeat=j)
  }

  for i in range(m):
    for j in range(k):
      W = numpy.zeros(q, dtype=numpy.float64)
      for x in range(1,q):

        # The original paper uses Gray code order to achieve constant
        # time updates per changing x_r, but for this problem we can
        # simply iterate in the default order and increase complexity
        # by factor `k`, since constructing ssf takes less time than
        # running the pattern matching algorithm (k in this algorithm
        # is log m in the pattern matching problem).
        for x_r in itertools.product(range(q), repeat=j):
          v = (-modular_inverse[x])*sum(G[i][t]*x_r[t] for t in range(j)) % q
          c = number_of_non_zeroes_in_Gy[tuple(x_r) + (x,)]
          # Above line does the same as the commented code listed below,
          # but has a better complexity, since it uses some memoization
          #
          # y = numpy.array(list(x_r)+[x]+[0]*(k-j-1))
          # Gy = G@y
          # c2 = sum(Gy[t]%q != 0 for t in range(i))
          # assert c == c2

          W[v] -= binom.pmf(numpy.floor(delta*m-c), m-j, 1-1/q)

      G[i][j] = numpy.argmax(W)

    # after selecting whole row G[i] update number of non zeroes
    for j in range(k):
      for x in range(1,q):
        for x_r in itertools.product(range(q), repeat=j):
          if numpy.dot(G[i][:j+1], list(x_r)+[x])%q != 0:
            number_of_non_zeroes_in_Gy[tuple(x_r)+(x,)] += 1
  return G
