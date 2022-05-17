import numpy as np
import scipy
from scipy import signal

def __get_clifford_array(text_mapped, word_mapped_reversed, positional):
  indices = np.ones(len(text_mapped)) if not positional else np.arange(len(text_mapped))
 
  first_component = scipy.signal.convolve(
    word_mapped_reversed**3, indices*text_mapped, mode = 'valid', method = 'fft')
  second_component = scipy.signal.convolve(
    word_mapped_reversed**2, indices*text_mapped**2, mode = 'valid', method = 'fft')
  third_component = scipy.signal.convolve(
    word_mapped_reversed, indices*text_mapped**3, mode = 'valid', method = 'fft', )

  return np.rint(first_component - 2*second_component + third_component).astype(int)


def correlation_correction_at(i, mismatch_positions_in_text, text_mapped, word_mapped_reversed, clifford_array):    
  correlation_correction = 0
  for mismatch_pos in mismatch_positions_in_text:
      if mismatch_pos is not None and mismatch_pos < len(text_mapped):
        tv = text_mapped[mismatch_pos]
        wv = word_mapped_reversed[len(word_mapped_reversed)-1+i-mismatch_pos]
        correlation_correction += tv*wv*(tv-wv)**2

  return correlation_correction

def are_all_mismatches_found_at(i, mismatch_positions_in_text, text_mapped, word_mapped_reversed, clifford_array):    
  return correlation_correction_at(i, mismatch_positions_in_text, text_mapped, word_mapped_reversed,clifford_array) == clifford_array[i]


def one_hamming_mismatch(text_mapped, word_mapped_reversed):
  a0 = __get_clifford_array(text_mapped, word_mapped_reversed, False)
  a1 = __get_clifford_array(text_mapped, word_mapped_reversed, True)

  possible_mismatch_position_in_text = [None if x0 == 0 else x1//x0 for x0,x1 in zip(a0,a1)]
  mismatch_position = [
    x if are_all_mismatches_found_at(i, [x], text_mapped, word_mapped_reversed, a0) else 'too many mismatches' 
    for i,x in enumerate(possible_mismatch_position_in_text)
  ]
  return mismatch_position

def nonrecursive(text_mapped, word_mapped_reversed, k):
  n = len(text_mapped)
  sample_rate = 1/max(k,1)
  mismatches = [set() for _ in range(n-len(word_mapped_reversed)+1)]

  for it in range(10*(int(k*np.log(n))+1)):
    masked_word = np.array([x if np.random.random() < sample_rate else 0 for x in word_mapped_reversed])
    found_mismatches = one_hamming_mismatch(text_mapped, masked_word)
    for i, x in enumerate(found_mismatches):
        if x is not None and x != "too many mismatches":
          mismatches[i].add(x)

  clifford_array = __get_clifford_array(text_mapped, word_mapped_reversed, False)
  number_of_mismatches = [
    len(x) if are_all_mismatches_found_at(i, x, text_mapped, word_mapped_reversed, clifford_array) else 'too many mismatches'
    for i,x in enumerate(mismatches)
  ]

  found = [i for i,x in enumerate(number_of_mismatches) if x != 'too many mismatches' and x <= k]
  yield from found


def preprocess(text, word):
  A = set(list(text[1:] + word[1:])) - set('?')
  letter_mapping = {c: i for i, c in enumerate(A, start = 1)}
  letter_mapping.update({'?': 0})
  return np.array([letter_mapping.get(c) for c in text[1:]]), np.array([letter_mapping.get(c) for c in word[:0:-1]])

def nonrecursivee(text, word, n, m, k):
  if m > n:
    yield from ()
  elif k >= m:
    yield from range(1, m+1)
  else:
    t, w = preprocess(text, word)
    yield from map(lambda x: x+1, nonrecursive(t, w, k))

