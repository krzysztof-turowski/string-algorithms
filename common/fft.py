import itertools

import scipy.signal
import sympy

def scipy_convolve(first_sequence, second_sequence):
  '''Convolution using floating-point FFT from scipy'''
  return scipy.signal.convolve(
      first_sequence, second_sequence, mode = 'valid', method = 'fft')

def integer_convolve(first_sequence, second_sequence):
  '''Exact convolution of integer sequences using FFT modulo a prime chosen
  for the input'''
  longer = [int(value) for value in first_sequence]
  shorter = [int(value) for value in second_sequence]
  if len(longer) < len(shorter):
    longer, shorter = shorter, longer
  longer_length, shorter_length = len(longer), len(shorter)
  maximum_value = (max(map(abs, longer)) * max(map(abs, shorter))
                   * shorter_length)
  size = 1 << max((longer_length - 1).bit_length(), 1)
  prime, root = _find_prime(size, 2 * maximum_value + 1)
  longer_transform = fft(longer + [0] * (size - longer_length), prime, root)
  shorter_transform = fft(shorter + [0] * (size - shorter_length), prime, root)
  convolution = ifft([first * second % prime for first, second
                      in zip(longer_transform, shorter_transform)], prime, root)
  return [value - prime if value > prime // 2 else value
          for value in convolution[shorter_length - 1:longer_length]]

def fft_boolean(first_sequence, second_sequence):
  """Exact Boolean convolution of nonempty binary sequences, in valid mode."""
  return [value != 0 for value in
          integer_convolve(first_sequence, second_sequence)]

def fft(sequence, prime, root):
  '''FFT modulo prime, root has to have order len(sequence) modulo prime'''
  return _transform(sequence, root, prime)

def ifft(sequence, prime, root):
  '''Inverse of fft'''
  transformed = _transform(sequence, pow(root, -1, prime), prime)
  size_inverse = pow(len(sequence), -1, prime)
  return [value * size_inverse % prime for value in transformed]

def _find_prime(size, lower_bound):
  '''Returns prime = multiplier * size + 1 >= lower_bound and a root of
  unity of order size modulo prime; size has to be a power of 2'''
  multiplier = max(-(-(lower_bound - 1) // size), 1)
  while not sympy.isprime(multiplier * size + 1):
    multiplier += 1
  prime = multiplier * size + 1
  roots = (pow(generator, multiplier, prime)
           for generator in itertools.count(2))
  return prime, next(
    root for root in roots if pow(root, size // 2, prime) == prime - 1)

def _transform(sequence, root, prime):
  size = len(sequence)
  if size == 0 or size & (size - 1):
    raise ValueError('Sequence length must be a positive power of two')
  sequence = list(sequence)
  reversed_index = 0
  for index in range(1, size):
    bit = size >> 1
    while reversed_index & bit:
      reversed_index ^= bit
      bit >>= 1
    reversed_index |= bit
    if index < reversed_index:
      sequence[index], sequence[reversed_index] = \
          sequence[reversed_index], sequence[index]
  block_length = 2
  while block_length <= size:
    half_length = block_length // 2
    block_root = pow(root, size // block_length, prime)
    for block_start in range(0, size, block_length):
      twiddle_factor = 1
      for offset in range(half_length):
        even_value = sequence[block_start + offset]
        odd_value = (sequence[block_start + offset + half_length]
                     * twiddle_factor % prime)
        sequence[block_start + offset] = (even_value + odd_value) % prime
        sequence[block_start + offset + half_length] = \
            (even_value - odd_value) % prime
        twiddle_factor = twiddle_factor * block_root % prime
    block_length <<= 1
  return sequence
