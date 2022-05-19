import os
import unittest

from compression import lpf
from generator import rand


class TestLPF(unittest.TestCase):
  run_large = unittest.skipUnless(
    os.environ.get('LARGE', False), 'Skip test in small runs')

  def check_input(self, text, answer=None):
    n = len(text)
    text = '#' + text
    answer = answer or lpf.naive(text, n)

    alg0 = lpf.naive(text, n)
    alg1 = lpf.chrochemore_ille_smith(text, n)
    alg2 = lpf.chrochemore_ille_smith_no_stack(text, n)

    self.assertEqual(alg0, answer)
    self.assertEqual(alg1, answer)
    self.assertEqual(alg2, answer)

  def test_lpf_corners(self):
    self.check_input('', [-1])
    self.check_input('a', [-1, 0])
    self.check_input('aa', [-1, 0, 1])
    self.check_input('ab', [-1, 0, 0])
    self.check_input('aaaa', [-1, 0, 3, 2, 1])
    self.check_input('abab', [-1, 0, 0, 2, 1])
    self.check_input('abbaabbbaaabab')
    self.check_input('ababcbababaa')
    self.check_input('eacacad')
    self.check_input('aacaacabcabaaac')
    self.check_input('abaab')
    self.check_input('aabbbbc')

  @run_large
  def test_lpf_random(self):
    T, n, A = 100, 500, ['a', 'b', 'c']
    for _ in range(T):
      text = rand.random_word(n, A)
      self.check_input(text)
