import itertools
import math
import random

from common import gf2
from common.fft import integer_convolve

def naive(text, word, n, m):
  if m == 0 or n < m:
    return

  for i in range(n - m + 1):
    if all(text[i + j] == word[j] or text[i + j] == '?' or word[j] == '?'
           for j in range(1, m + 1)):
      yield i + 1

def basic_fft(text, word, n, m, fft = integer_convolve):
  if n < m:
    return
  A = set(text[1:] + word[1:]) - set('?')
  mismatches = [0] * (n - m + 1)
  for first_letter in A:
    masked_text = [int(c == first_letter) for c in text[1:]]
    for second_letter in A:
      if first_letter != second_letter:
        masked_word = [int(c == second_letter) for c in reversed(word[1:])]
        mismatches_ab = fft(masked_text, masked_word)
        mismatches = [x + y for x, y in zip(mismatches, mismatches_ab)]
  yield from (index + 1 for index, is_mismatch in enumerate(mismatches)
              if is_mismatch == 0)

def fft_by_parts(text, word, n, m, algorithm, fft = integer_convolve):
  def _compute_part(index, part):
    return [
        index * m + i for i in algorithm(part, word, len(part) - 1, m, fft)]

  if m == 0 or n < m:
    return
  parts = ['#' + text[i * m + 1:(i + 2) * m + 1]
           for i in range(math.ceil(n / m))]
  results = (_compute_part(index, part) for index, part in enumerate(parts))
  yield from sorted(set(index for result in results for index in result))

def clifford_clifford(text, word, n, m, fft = integer_convolve):
  def _times(x, y):
    return list(itertools.starmap(lambda a, b: a * b, zip(x, y)))

  if m == 0 or n < m:
    return
  A = set(text[1:] + word[1:]) - set('?')
  letter_map = {c: i for i, c in enumerate(A, start = 1)}
  letter_map.update({'?': 0})
  text = [letter_map.get(c) for c in text[1:]]
  word = [letter_map.get(c) for c in word[:0:-1]]

  first_component = fft(_times(word, _times(word, word)), text)
  second_component = fft(_times(word, word), _times(text, text))
  third_component = fft(word, _times(text, _times(text, text)))
  result = [
    first - 2 * second + third
    for first, second, third in zip(
        first_component, second_component, third_component)]
  yield from (index + 1 for index, value in enumerate(result) if value == 0)

def fischer_paterson(text, word, n, m):
  def _pack(sequence):
    return sum(1 << (index * buffer_bit_length)
               for index, value in enumerate(sequence) if value)

  if m == 0 or n < m:
    return
  A = set(text[1:] + word[1:]) - set('?')
  buffer_bit_length = m.bit_length()
  mask = (1 << buffer_bit_length) - 1
  mismatches = [0] * (n + m - 1)

  for first_letter, second_letter in itertools.permutations(A, 2):
    masked_text = [int(c == first_letter) for c in text[1:]]
    masked_word = [int(c == second_letter) for c in word[:0:-1]]
    product = _pack(masked_text) * _pack(masked_word)
    for index in range(n + m - 1):
      mismatches[index] += (product >> (index * buffer_bit_length)) & mask

  yield from (index + 1 for index, value in enumerate(mismatches[m - 1:n])
              if value == 0)

def indyk(text, word, n, m, c = 7, fft = integer_convolve):
  def f(letter, index):
    return letter_map[letter][index] if letter != '?' else 0

  def g(letter, index):
    return 1 - letter_map[letter][index] if letter != '?' else 0

  if m == 0 or n < m:
    return
  A = set(text[1:] + word[1:]) - set('?')
  d = math.ceil(c * math.log2(max(n, 2)))
  letter_map = {c: [random.randint(0, 1) for _ in range(d)] for c in A}
  text, word = text[1:], word[:0:-1]
  mismatches = [0] * (n - m + 1)

  for index in range(d):
    masked_text = [f(c, index) for c in text]
    masked_word = [g(c, index) for c in word]
    mismatches = [first + second for first, second
                  in zip(mismatches, fft(masked_text, masked_word))]

  yield from (index + 1 for index, value in enumerate(mismatches) if value == 0)

def indyk_gf2(text, word, n, m, c = 16):
  if m == 0 or n < m:
    return
  A = set(text[1:] + word[1:]) - set('?')
  d = math.ceil(c * math.log2(max(n, 2)))
  letter_map = {c: random.getrandbits(d) for c in A}
  text, word = text[1:], word[:0:-1]
  shifts_mask = (1 << (n - m + 1)) - 1
  mismatches = 0

  for index in range(d):
    text_map = {c: str(1 - (letter_map[c] >> index & 1)) for c in A}
    word_map = {c: str(letter_map[c] >> index & 1) for c in A}
    text_map.update({'?': '0'})
    word_map.update({'?': '0'})
    text_bits = int(text.translate(str.maketrans(text_map))[::-1], 2)
    word_bits = int(word.translate(str.maketrans(word_map))[::-1], 2)
    word_bits &= random.getrandbits(m)
    mismatches |= gf2.multiply(text_bits, word_bits) >> (m - 1) & shifts_mask

  yield from (index + 1 for index in range(n - m + 1)
              if not mismatches >> index & 1)

def sperner(text, word, n, m, fft = integer_convolve):
  if m == 0 or n < m:
    return
  A = set(text[1:] + word[1:]) - set('?')
  k = 1
  while math.comb(k, k // 2) < len(A):
    k += 1
  letter_map = {c: set(subset) for c, subset in
                    zip(A, itertools.combinations(range(k), k // 2))}
  text, word = text[1:], word[:0:-1]
  mismatches = [0] * (n - m + 1)

  for index in range(k):
    masked_text = [int(c != '?' and index in letter_map[c]) for c in text]
    masked_word = [int(c != '?' and index not in letter_map[c])
                   for c in word]
    mismatches = [first + second for first, second
                  in zip(mismatches, fft(masked_text, masked_word))]

  yield from (index + 1 for index, value in enumerate(mismatches) if value == 0)

def kalai(text, word, n, m, convolve = integer_convolve):
  if m == 0 or n < m:
    return
  A = set(text[1:] + word[1:]) - set('?')
  letter_map = {c: i for i, c in enumerate(A, start = 1)}
  letter_map.update({'?': 0})
  text = [letter_map.get(c) for c in text[1:]]
  word = [letter_map.get(c) for c in word[:0:-1]]
  weights = [random.randint(1, n**2 + 1) if value else 0 for value in word]

  first_component = convolve(text, weights)
  second_component = convolve(
    [int(value != 0) for value in text],
    [value * weight for value, weight in zip(word, weights)])
  result = [
    first - second for first, second in zip(first_component, second_component)]
  yield from (index + 1 for index, value in enumerate(result) if value == 0)
