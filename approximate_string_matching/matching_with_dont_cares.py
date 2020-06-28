from itertools import starmap
import scipy.signal

def times(x, y):
  return list(starmap(lambda a, b: a * b, zip(x, y)))

def convolve(x, y):
  return scipy.signal.convolve(x, y, mode = 'valid', method = 'fft')

def exact_matching_with_dont_cares(text, pattern, n, m):
  if n < m:
    return

  text, pattern = text[1:], pattern[:0:-1]
  alphabet = set(list(text + pattern))
  alphabet.discard('?')

  letter_mapping = {'?': 0}
  letter_mapping.update(
    {letter: index for index, letter in enumerate(alphabet, start = 1)})

  text = list(map(letter_mapping.get, text))
  pattern = list(map(letter_mapping.get, pattern))
  mapped_text = list(map(lambda x: int(x != 0), text))
  mapped_pattern = list(map(lambda x: int(x != 0), pattern))

  first_component = convolve(
      times(mapped_pattern, times(pattern, pattern)),
      mapped_text
  )
  second_component = convolve(
      times(mapped_pattern, pattern),
      times(mapped_text, text)
  )
  third_component = convolve(
      mapped_pattern,
      times(mapped_text,times(text,text))
  )

  result = [first - 2 * second + third for first, second, third in
            zip(first_component, second_component, third_component)]

  yield from (index + 1 for index, value in enumerate(result) if value == 0)
