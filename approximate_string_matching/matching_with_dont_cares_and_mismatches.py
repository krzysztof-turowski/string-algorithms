import numpy as np
from scipy import signal

def __get_clifford_array(text_mapped, word_mapped, positional):
  indices = np.ones(len(text_mapped)) if not positional else np.arange(len(text_mapped))
 
  first_component = signal.convolve(
    (word_mapped**3)[::-1], indices*text_mapped, mode = 'valid', method = 'fft')
  second_component = signal.convolve(
    (word_mapped**2)[::-1], indices*text_mapped**2, mode = 'valid', method = 'fft')
  third_component = signal.convolve(
    (word_mapped)[::-1], indices*text_mapped**3, mode = 'valid', method = 'fft', )

  return np.rint(first_component - 2*second_component + third_component).astype(int)

def __are_all_mismatches_found_at(i, mismatch_positions_in_text, text_mapped, word_mapped, clifford_array):    
  correlation_correction = 0
  for mismatch_pos in mismatch_positions_in_text:
      if mismatch_pos is not None and mismatch_pos < len(text_mapped) and mismatch_pos-i < len(word_mapped):
        tv = text_mapped[mismatch_pos]
        wv = word_mapped[mismatch_pos-i]
        correlation_correction += tv*wv*(tv-wv)**2

  return correlation_correction == clifford_array[i]

def one_hamming_mismatch(text_mapped, word_mapped, corrections=[]):
  a0 = __get_clifford_array(text_mapped, word_mapped, False)
  a1 = __get_clifford_array(text_mapped, word_mapped, True)

  for j, corrections_at_j in enumerate(corrections):
    if word_mapped[j] != 0:
      for i in corrections_at_j:
        tv = text_mapped[i+j]
        wv = word_mapped[j]
        a0[i] -= tv*wv*(tv-wv)
        a1[i] -=  i*tv*wv*(tv-wv) 

  possible_mismatch_position_in_text = [None if x0 == 0 else x1//x0 for x0,x1 in zip(a0,a1)]
  mismatch_position = [
    x if __are_all_mismatches_found_at(i, [x], text_mapped, word_mapped, a0) else 'too many mismatches' 
    for i,x in enumerate(possible_mismatch_position_in_text)
  ]
  return mismatch_position


def apply_preprocessing(func):
  def wrapper(text, word, n, m, k, *args, **kwargs):
    if m > n:
      yield from ()
    else:
      # map characters to numbers, such that don't care is 0
      alphabet = set(list(text[1:] + word[1:])) - set('?')
      letter_mapping = {c: i for i, c in enumerate(alphabet, start = 1)}
      letter_mapping.update({'?': 0})

      # remove sharps, since signal.convolve requires 0-indexing
      text = np.array([letter_mapping.get(c) for c in text[1:]])
      word = np.array([letter_mapping.get(c) for c in word[1:]])

      yield from map(lambda x: x+1, func(text, word, n, m, k, *args, **kwargs))

  return wrapper


@apply_preprocessing
def nonrecursive(text_mapped, word_mapped, n, m, k):
  sample_rate = 1/max(k,1)
  mismatches = [set() for _ in range(n-m+1)]

  for it in range(int(k*(40+np.log(n)))):
    masked_word = np.array([x if np.random.random() < sample_rate else 0 for x in word_mapped])
    found_mismatches = one_hamming_mismatch(text_mapped, masked_word)
    for i, x in enumerate(found_mismatches):
        if x is not None and x != "too many mismatches" and len(mismatches[i]) < k:
          mismatches[i].add(x)

  yield from __checking_stage(text_mapped, word_mapped, mismatches)

@apply_preprocessing
def recursive(text_mapped, word_mapped, n, m, k):
  mismatches = [set() for _ in range(n-m+1)]
  E = [set() for _ in range(m)]

  ks = k
  while ks >= 1:
    sample_rate = 1/ks
    for it in range(40*int(ks + np.log(n))):
      masked_word = np.array([x if np.random.random() < sample_rate else 0 for x in word_mapped])
      found_mismatches = one_hamming_mismatch(text_mapped, masked_word, corrections=E)
      
      for i, x in enumerate(found_mismatches):
        if x is not None and x != "too many mismatches" and len(mismatches[i]) < k:
          mismatches[i].add(x)
          E[x-i].add(i)

      ks /= 2

  yield from __checking_stage(text_mapped, word_mapped, mismatches)


def __checking_stage(text_mapped, word_mapped, mismatches):
  clifford_array = __get_clifford_array(text_mapped, word_mapped, False)
  number_of_mismatches = [
    len(x) if __are_all_mismatches_found_at(i, x, text_mapped, word_mapped, clifford_array) else 'too many mismatches'
    for i,x in enumerate(mismatches)
  ]
  return [i for i,x in enumerate(number_of_mismatches) if x != 'too many mismatches']

