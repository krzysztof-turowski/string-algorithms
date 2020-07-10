import itertools
import math
import scipy.signal

def basic_fft(text, word, n, m):
  if n < m:
    return
  alphabet = set(list(text[1:] + word[1:])) - set('?')
  mismatches = [0] * (n - m + 1)
  for first_letter in alphabet:
    masked_text = [int(current_char == first_letter) for current_char in
                   text[1:]]
    for second_letter in alphabet:
      if first_letter != second_letter:
        masked_word = [int(current_char == second_letter)
                       for current_char in reversed(word[1:])]
        mismatches_ab = scipy.signal.convolve(
            masked_text, masked_word, mode = 'valid', method = 'fft')
        mismatches = [x + y for x, y in zip(mismatches, mismatches_ab)]
  yield from (index + 1 for index, is_mismatch in enumerate(mismatches)
              if is_mismatch == 0)

def clifford_clifford_parts(text, word, n, m):
  def _compute_part(index, part):
    return [index * m + i
            for i in clifford_clifford(part, word, len(part) - 1, m)]

  if n < m:
    return
  parts = ['#' + text[i * m + 1:(i + 2) * m + 1]
           for i in range(math.ceil(n / m))]
  results = (_compute_part(index, part) for index, part in enumerate(parts))
  yield from sorted(set(index for result in results for index in result))

def clifford_clifford(text, word, n, m):
  def _times(x, y):
    return list(itertools.starmap(lambda a, b: a * b, zip(x, y)))

  if n < m:
    return
  alphabet = set(list(text[1:] + word[1:])) - set('?')
  letter_mapping = {'?': 0}
  letter_mapping.update(
      {letter: index for index, letter in enumerate(alphabet, start = 1)})
  text = [letter_mapping.get(c) for c in text[1:]]
  word = [letter_mapping.get(c) for c in word[:0:-1]]
  masked_text = [int(v != 0) for v in text]
  masked_word = [int(v != 0) for v in word]

  first_component = scipy.signal.convolve(
      _times(masked_word, _times(word, word)), masked_text,
      mode = 'valid', method = 'fft')
  second_component = scipy.signal.convolve(
      _times(masked_word, word), _times(masked_text, text),
      mode = 'valid', method = 'fft')
  third_component = scipy.signal.convolve(
      masked_word, _times(masked_text, _times(text, text)),
      mode = 'valid', method = 'fft')
  result = [first - 2 * second + third for first, second, third in
            zip(first_component, second_component, third_component)]
  yield from (index + 1 for index, value in enumerate(result) if value == 0)
