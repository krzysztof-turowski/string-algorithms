import scipy.signal

def basic_fft(text, word, n, m):
  if n < m:
    return
  A = set(list(text[1:] + word[1:]))
  A.discard('?')
  mismatches = [0] * (n - m + 1)
  for a in A:
    text_a_mask = [int(c == a) for c in text[1:]]
    for b in A:
      if a != b:
        word_b_mask = [int(c == b) for c in reversed(word[1:])]
        mismatches_ab = scipy.signal.convolve(
            text_a_mask, word_b_mask, mode = 'valid', method = 'fft')
        mismatches = [x + y for x, y in zip(mismatches, mismatches_ab)]
  yield from (i + 1 for i, v in enumerate(mismatches) if v == 0)
