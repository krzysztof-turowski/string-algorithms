import unittest
import os
from random import randint

from longest_common_subsequence.myers import (
    longest_common_substring, brute_force_lcs)
from generator.rand import random_word

def validate_text_lcs(text, lcs):
  it = iter(text)
  return all(any(c == ch for c in it) for ch in lcs)

def validate_lcs(text_a, text_b, lcs):
  return (validate_text_lcs(text_a, lcs) and
          validate_text_lcs(text_b, lcs))


class TestMyers(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def test_myers_example_case(self):
    text_a, text_b = '#abcabba', '#cbabac'
    text_lcs = longest_common_substring(
        text_a, text_b,
        len(text_a) - 1, len(text_b) - 1
    )
    self.assertTrue(validate_lcs(text_a, text_b, text_lcs))
    self.assertEqual(len(text_lcs), 4)

  def test_myers_full_lcs(self):
    text_a, text_b = '#aaaaaaa', '#aaaaa'
    text_lcs = longest_common_substring(
        text_a, text_b,
        len(text_a) - 1, len(text_b) - 1
    )
    self.assertTrue(
        validate_lcs(
            text_a, text_b, text_lcs) and
        len(text_lcs) == 5
    )

  def test_myers_empty_lcs(self):
    text_a, text_b = '#aaaaaaa', '#bbbbbb'
    text_lcs = longest_common_substring(
        text_a, text_b,
        len(text_a) - 1, len(text_b) - 1
    )
    self.assertEqual(text_lcs, '')

  @run_large
  def test_big_texts(self):
    a_len, alphabet = 1000000, ['a', 'b','c']
    text_a = random_word(a_len, alphabet)
    text_b = text_a + random_word(100, alphabet)
    text_a = text_a + 'eeeeeeeeee'
    text_lcs = longest_common_substring(
        text_a, text_b,
        len(text_a) - 1, len(text_b) - 1
    )
    self.assertTrue(
        validate_lcs(
            text_a, text_b, text_lcs
        ) and
        len(text_lcs) == a_len
    )

  def test_myers_random_extensions(self):
    a_len, alphabet = 10000, ['a', 'b', 'c', 'd', 'e']
    text_a = random_word(a_len, alphabet)
    text_b = text_a
    diff = randint(50, 100)
    for _ in range(diff):
      place = randint(0, a_len - 1)
      extension = random_word(randint(1, 5), alphabet)
      text_b = text_b[:place] + extension + text_b[place:]

    text_lcs = longest_common_substring(
        text_a, text_b,
        len(text_a) - 1, len(text_b) - 1
    )
    self.assertTrue(
        validate_lcs(
            text_a, text_b, text_lcs
        ) and
        len(text_lcs) == a_len
    )

  def test_myers_random_short(self):
    iter_count, a_len, b_len = 50, 100, 100
    alphabet = ['a', 'b', 'c', 'd', 'e']
    solutions = []
    for _ in range(iter_count):
      text_a = random_word(a_len, alphabet)
      text_b = random_word(b_len, alphabet)

      text_lcs = longest_common_substring(
          text_a, text_b,
          len(text_a) - 1, len(text_b) - 1
      )
      brute_lcs = brute_force_lcs(
          text_a, text_b,
          len(text_a) - 1, len(text_b) - 1
      )

      valid = (
          validate_lcs(
              text_a, text_b, text_lcs
          ) and
          len(text_lcs) == len(brute_lcs)
      )

      solutions.append(valid)
    self.assertListEqual([True] * iter_count, solutions)

  @run_large
  def test_myers_random_lengths(self):
    iter_count, a_len, b_len = 10, randint(400, 1000), randint(400, 1000)
    alphabet = ['a', 'b', 'c']
    solutions = []
    for _ in range(iter_count):
      text_a = random_word(a_len, alphabet)
      text_b = random_word(b_len, alphabet)

      text_lcs = longest_common_substring(
          text_a, text_b,
          len(text_a) - 1, len(text_b) - 1
      )
      brute_lcs = brute_force_lcs(
          text_a, text_b,
          len(text_a) - 1, len(text_b) - 1
      )

      valid = (
          validate_lcs(
              text_a, text_b, text_lcs
          ) and
          len(text_lcs) == len(brute_lcs)
      )

      solutions.append(valid)
    self.assertListEqual([True] * iter_count, solutions)
