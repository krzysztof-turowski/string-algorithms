import unittest
import os
import math
import random

from approx_shortest_superstring.approximate_shortest_superstring \
import shortest_common_super_approx

from approx_shortest_superstring.exact_bruteforce \
import shortest_common_super
from generator import rand

class TestCommentzWalter(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_superstring(self, result, words):
    self.assertTrue(all(word[1:] in result for word in words))

  def check_length(self, result, words, alphabet):
    optimal_length = len(shortest_common_super(words, alphabet)) - 1
    approximated_length = len(result) - 1
    bound = math.ceil(math.log(optimal_length)+1) * 2 * optimal_length
    self.assertTrue(bound > approximated_length)

  def test_single_word(self):
    input_words = ["#abc"]
    result = shortest_common_super_approx(input_words)
    self.check_superstring(result, input_words)
    self.check_length(result, input_words, ["a", "b", "c"])

  def test_words_with_substrings(self):
    input_words = ["#abc", "#ab", "#c"]
    result = shortest_common_super_approx(input_words)
    self.check_superstring(result, input_words)
    self.check_length(result, input_words, ["a", "b", "c"])

  def test_single_letters(self):
    input_words = ["#a", "#b", "#c", "#d", "#e", "#f", "#g"]
    result = shortest_common_super_approx(input_words)
    self.check_superstring(result, input_words)

  def test_small(self):
    input_words = ["#abc", "#bca", "#cab", "#d"]
    result = shortest_common_super_approx(input_words)
    self.check_superstring(result, input_words)
    self.check_length(result, input_words, ["a", "b", "c", "d"])

  def test_big_words_length(self):
    input_words = ["#" + "a" * 200, "#" + "b" * 300, "#" + "c" * 500]
    result = shortest_common_super_approx(input_words)
    self.check_superstring(result, input_words)
    self.assertTrue(len(result) < 2000)

  @run_large
  def test_many_abc_small_words(self):
    T, alphabet = 1000, ["a", "b", "c"]
    for _ in range(T):
      amount = random.randint(2, 4)
      input_words = [rand.random_word(random.randint(1, 4), alphabet)\
      for _ in range(amount)]
      result = shortest_common_super_approx(input_words)
      self.check_superstring(result, input_words)
      self.check_length(result, input_words, alphabet)

  @run_large
  def test_random_words(self):
    T, alphabet = 100, ["a", "b", "c", "d"]
    for _ in range(T):
      amount = random.randint(5, 50)
      input_words = [rand.random_word(random.randint(20, 300), alphabet) for\
      _ in range(amount)]
      result = shortest_common_super_approx(input_words)
      self.check_superstring(result, input_words)
