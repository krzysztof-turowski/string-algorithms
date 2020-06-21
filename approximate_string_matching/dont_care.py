import scipy.signal

def basic_fft(text, word, n, m):
  if n < m:
    return
  alphabet = set(list(text[1:] + word[1:]))
  alphabet.discard('?')
  mismatches = [0] * (n - m + 1)
  for first_letter in alphabet:
    masked_text = [int(current_char == first_letter) for current_char in
                   text[1:]]
    for second_letter in alphabet:
      if first_letter != second_letter:
        masked_word = [int(current_char == second_letter) for current_char in
                       reversed(word[1:])]
        mismatches_ab = scipy.signal.convolve(
            masked_text, masked_word, mode = 'valid', method = 'fft')
        mismatches = [x + y for x, y in zip(mismatches, mismatches_ab)]
  yield from (index + 1 for index, is_mismatch in enumerate(mismatches) if
              is_mismatch == 0)
