import os
import random
import unittest

from common import fft, gf2, prefix

class TestCommon(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def test_overlap(self):
    self.assertEqual(prefix.get_overlap('#aba','#bab'), 2)
    self.assertEqual(prefix.get_overlap('#abab','#bab'), 3)
    self.assertEqual(prefix.get_overlap('#abb','#ab'), 0)
    self.assertEqual(prefix.get_overlap('#aa','#aa'), 1)
    self.assertEqual(prefix.get_overlap('#aab','#aab'), 0)
    self.assertEqual(prefix.get_overlap('#undergrounder', '#undergrounder'), 5)

  @staticmethod
  def naive_convolution(first, second):
    if len(first) < len(second):
      first, second = second, first
    return [sum(first[shift + index] * value
                for index, value in enumerate(reversed(second)))
            for shift in range(len(first) - len(second) + 1)]

  @staticmethod
  def naive_gf2_multiply(first, second):
    product = 0
    for bit in range(second.bit_length()):
      if second >> bit & 1:
        product ^= first << bit
    return product

  def test_fft_round_trip(self):
    for size in (1, 2, 4, 8, 16):
      with self.subTest(size = size):
        sequence = list(range(size))
        root = pow(3, 16 // size, 17)
        self.assertEqual(fft.ifft(fft.fft(sequence, 17, root), 17, root),
                         sequence)

  def test_fft_rejects_invalid_lengths(self):
    for transform in (fft.fft, fft.ifft):
      for size in (0, 3, 5, 6, 7, 9):
        with self.subTest(transform = transform.__name__, size = size):
          with self.assertRaisesRegex(ValueError, 'power of two'):
            transform([0] * size, 17, 3)

  def test_gf2_field_cache(self):
    # pylint: disable=protected-access
    self.assertIs(gf2._field(16), gf2._field(16))

  def test_integer_convolve(self):
    self.assertEqual(fft.integer_convolve([1, 2, 3, 4], [1, 1]), [3, 5, 7])
    self.assertEqual(fft.integer_convolve([1, 1], [1, 2, 3, 4]), [3, 5, 7])
    self.assertEqual(fft.integer_convolve([-2, 5], [3]), [-6, 15])
    self.assertEqual(fft.integer_convolve([0, 0, 0], [0, 0]), [0, 0])

  def test_integer_convolve_random(self):
    for _ in range(200):
      bound = random.choice([1, 10**6, 10**30])
      first = [random.randint(-bound, bound)
               for _ in range(random.randint(1, 40))]
      second = [random.randint(-bound, bound)
                for _ in range(random.randint(1, 40))]
      self.assertEqual(fft.integer_convolve(first, second),
                       self.naive_convolution(first, second))

  @run_large
  def test_integer_convolve_large_values(self):
    n, m = 40000, 20000
    self.assertEqual(fft.integer_convolve([97] * n, [n**2] * m),
                     [97 * n**2 * m] * (n - m + 1))

  def test_gf2_multiply(self):
    self.assertEqual(gf2.multiply(0b11, 0b111), 0b1001)
    self.assertEqual(gf2.multiply(0b101, 0), 0)
    self.assertEqual(gf2.multiply(1, 0b1011), 0b1011)

  def test_gf2_multiply_random(self):
    for _ in range(200):
      first = random.getrandbits(random.randint(1, 500))
      second = random.getrandbits(random.randint(1, 500))
      self.assertEqual(gf2.multiply(first, second),
                       self.naive_gf2_multiply(first, second))

  @run_large
  def test_gf2_multiply_long(self):
    first, second = random.getrandbits(40000), random.getrandbits(20000)
    self.assertEqual(gf2.multiply(first, second),
                     self.naive_gf2_multiply(first, second))
