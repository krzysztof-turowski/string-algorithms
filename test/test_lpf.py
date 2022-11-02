import os
import string
import unittest

from string_indexing import lpf
from generator import rand


class TestLPF(unittest.TestCase):
  run_large = unittest.skipUnless(
    os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_input(self, text, reference, algorithm):
    n = len(text)
    t = '#' + text
    self.assertEqual(algorithm(t, n), reference)

  def check_input_forall(self, text, reference=None):
    if reference is None:
      reference = lpf.naive('#' + text, len(text))
    else:
      reference = [-1] + reference

    self.check_input(text, reference,
                     lpf.naive)
    self.check_input(text, reference,
                     lpf.crochemore_ilie_smyth)
    self.check_input(text, reference,
                     lpf.crochemore_ilie_smyth_no_stack)

  def test_lpf_corners(self):
    self.check_input_forall('', [])
    self.check_input_forall('a', [0])
    self.check_input_forall('aa', [0, 1])
    self.check_input_forall('ab', [0, 0])
    self.check_input_forall('aaaa', [0, 3, 2, 1])
    self.check_input_forall('abab', [0, 0, 2, 1])
    self.check_input_forall('abbaabbbaaabab')
    self.check_input_forall('ababcbababaa')
    self.check_input_forall('eacacad')
    self.check_input_forall('aacaacabcabaaac')
    self.check_input_forall('abaab')
    self.check_input_forall('aabbbbc')

  @run_large
  def test_lpf_random(self):
    T, n, A = 100, 500, ['a', 'b', 'c']
    for _ in range(T):
      text = rand.random_word(n, A)[1:]
      self.check_input_forall(text)

  @run_large
  def test_lpf_random_short_strings(self):
    T, n, A = 5, 500, ['a', 'b', 'c']
    for _ in range(T):
      text = rand.random_word(n, A)[1:]
      self.check_input_forall(text)

  @run_large
  def test_lpf_random_cyclic(self):
    T, n, A = 10, 200, ['a', 'b', 'c']
    for _ in range(T):
      text = rand.random_word(n, A)[1:]
      text = text * 10
      self.check_input_forall(text)

  @run_large
  def test_lpf_random_big_alphabet(self):
    T, n, A = 100, 500, string.ascii_letters + string.digits
    for _ in range(T):
      text = rand.random_word(n, A)[1:]
      self.check_input_forall(text)
