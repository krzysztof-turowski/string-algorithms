'''Multiplication of polynomials over GF(2) with Cantor's method (as in
Indyk's algorithm)'''

import functools
import itertools
import operator

import sympy

MINIMUM_FIELD_DEGREE = 16

def _polynomial_multiply(first, second):
  result = 0
  while second:
    if second & 1:
      result ^= first
    first, second = first << 1, second >> 1
  return result

def _polynomial_remainder(dividend, divisor):
  divisor_length = divisor.bit_length()
  while dividend.bit_length() >= divisor_length:
    dividend ^= divisor << (dividend.bit_length() - divisor_length)
  return dividend

def _is_irreducible(polynomial):
  coefficients = [int(bit) for bit in bin(polynomial)[2:]]
  return sympy.Poly(
      coefficients, sympy.Symbol('x'), modulus = 2).is_irreducible

# pylint: disable=too-few-public-methods
class _Field:
  '''GF(2^degree) with elements represented as polynomials over GF(2)'''

  def __init__(self, degree):
    self.degree = degree
    self.polynomial = next(
        (1 << degree) | lower for lower in range(1, 1 << degree, 2)
        if _is_irreducible((1 << degree) | lower))
    self.chunk_bits = degree // 4
    chunk_count = 1 << self.chunk_bits
    self.products = [_polynomial_multiply(first, second)
                     for first in range(chunk_count)
                     for second in range(chunk_count)]
    self.reductions = [_polynomial_remainder(high << degree, self.polynomial)
                       for high in range(chunk_count)]
    self.basis = self._cantor_basis()
    self.subspace_at_basis = [[self._subspace_value(level, element)
                               for element in self.basis]
                              for level in range(degree)]

  def multiply(self, first, second):
    first_chunks = self._chunks(first)
    second_chunks = self._chunks(second)
    product = 0
    for first_index, first_chunk in enumerate(first_chunks):
      for second_index, second_chunk in enumerate(second_chunks):
        chunk_product = self.products[
            first_chunk << self.chunk_bits | second_chunk]
        product ^= chunk_product << (
            self.chunk_bits * (first_index + second_index))
    return self._reduce(product)

  def _chunks(self, element):
    chunk_mask = (1 << self.chunk_bits) - 1
    return [element >> (self.chunk_bits * index) & chunk_mask
            for index in range(self.degree // self.chunk_bits)]

  def _reduce(self, product):
    chunk_mask = (1 << self.chunk_bits) - 1
    for index in range(self.degree // self.chunk_bits - 1, -1, -1):
      shift = self.degree + self.chunk_bits * index
      high = product >> shift & chunk_mask
      product ^= (high << shift) ^ (self.reductions[high]
                                    << (self.chunk_bits * index))
    return product

  def _cantor_basis(self):
    '''basis[0] = 1, basis[i]^2 + basis[i] = basis[i - 1]'''
    pivots = {}
    for bit in range(self.degree):
      image = self.multiply(1 << bit, 1 << bit) ^ (1 << bit)
      combination = 1 << bit
      while image:
        top = image.bit_length() - 1
        if top not in pivots:
          pivots[top] = (image, combination)
          break
        pivot_image, pivot_combination = pivots[top]
        image ^= pivot_image
        combination ^= pivot_combination
    basis = [1]
    for _ in range(1, self.degree):
      target, solution = basis[-1], 0
      while target:
        pivot_image, pivot_combination = pivots[target.bit_length() - 1]
        target, solution = target ^ pivot_image, solution ^ pivot_combination
      basis.append(solution)
    return basis

  def _subspace_value(self, level, element):
    '''s_level(element), where s_level vanishes on span(basis[0:level])'''
    powers = itertools.accumulate(
        range(level), lambda power, _: self.multiply(power, power),
        initial = element)
    return functools.reduce(operator.xor, (
        power for bit, power in enumerate(powers) if level & bit == bit), 0)

_FIELDS = {}

def _field(degree):
  if degree not in _FIELDS:
    _FIELDS[degree] = _Field(degree)
  return _FIELDS[degree]

def _subspace_exponents(level):
  return [1 << bit for bit in range(level + 1) if level & bit == bit]

def _coset_value(field, level, coset):
  '''Value of s_level at the sum of field.basis[index] over bits of coset'''
  return functools.reduce(operator.xor, (
      value for index, value in enumerate(field.subspace_at_basis[level])
      if coset >> index & 1), 0)

def _evaluate(field, polynomial, level, coset):
  '''Values of the polynomial of degree < 2^level at the points of
  coset + span(field.basis[0:level])'''
  if level == 0:
    return [polynomial[0]]
  half = 1 << (level - 1)
  polynomial = list(polynomial)
  lower_exponents = _subspace_exponents(level - 1)[:-1]
  for degree in range(2 * half - 1, half - 1, -1):
    coefficient = polynomial[degree]
    if coefficient:
      for exponent in lower_exponents:
        polynomial[degree - half + exponent] ^= coefficient
  remainder, quotient = polynomial[:half], polynomial[half:]
  # s_(level-1) is shift on the first half and shift + 1 on the second
  shift = _coset_value(field, level - 1, coset)
  low = [value ^ field.multiply(shift, quotient_value)
         for value, quotient_value in zip(remainder, quotient)]
  high = [value ^ quotient_value
          for value, quotient_value in zip(low, quotient)]
  return (_evaluate(field, low, level - 1, coset)
          + _evaluate(field, high, level - 1, coset | 1 << (level - 1)))

def _interpolate(field, values, level, coset):
  '''Inverse of _evaluate'''
  if level == 0:
    return [values[0]]
  half = 1 << (level - 1)
  low = _interpolate(field, values[:half], level - 1, coset)
  high = _interpolate(field, values[half:], level - 1,
                      coset | 1 << (level - 1))
  quotient = [low_value ^ high_value
              for low_value, high_value in zip(low, high)]
  shift = _coset_value(field, level - 1, coset)
  remainder = [value ^ field.multiply(shift, quotient_value)
               for value, quotient_value in zip(low, quotient)]
  polynomial = remainder + quotient
  for exponent in _subspace_exponents(level - 1)[:-1]:
    for degree, coefficient in enumerate(quotient):
      polynomial[degree + exponent] ^= coefficient
  return polynomial

def _field_degree(first_length, second_length):
  '''Smallest power of 2 k such that the product fits into 2^k blocks of
  k / 2 bits'''
  def block_count(degree):
    block_bits = degree // 2
    return (-(-first_length // block_bits)
            + -(-second_length // block_bits) - 1)

  degrees = (MINIMUM_FIELD_DEGREE << power for power in itertools.count())
  return next(degree for degree in degrees
              if block_count(degree) <= 1 << degree)

def _blocks(polynomial, block_bytes):
  data = polynomial.to_bytes(
      -(-polynomial.bit_length() // (8 * block_bytes)) * block_bytes, 'little')
  return [int.from_bytes(data[start:start + block_bytes], 'little')
          for start in range(0, len(data), block_bytes)]

def multiply(first, second):
  '''Product of polynomials over GF(2) given as Python integers (bit i is
  the coefficient of x^i)'''
  if first == 0 or second == 0:
    return 0
  degree = _field_degree(first.bit_length(), second.bit_length())
  field = _field(degree)
  block_bytes = degree // 16
  first_blocks = _blocks(first, block_bytes)
  second_blocks = _blocks(second, block_bytes)
  level = (len(first_blocks) + len(second_blocks) - 2).bit_length()
  size = 1 << level
  first_values = _evaluate(
      field, first_blocks + [0] * (size - len(first_blocks)), level, 0)
  second_values = _evaluate(
      field, second_blocks + [0] * (size - len(second_blocks)), level, 0)
  product_blocks = _interpolate(
      field, [field.multiply(first_value, second_value) for first_value,
              second_value in zip(first_values, second_values)], level, 0)
  even = int.from_bytes(b''.join(
      block.to_bytes(2 * block_bytes, 'little')
      for block in product_blocks[0::2]), 'little')
  odd = int.from_bytes(b''.join(
      block.to_bytes(2 * block_bytes, 'little')
      for block in product_blocks[1::2]), 'little')
  return even ^ (odd << (8 * block_bytes))
