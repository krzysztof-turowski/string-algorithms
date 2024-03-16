import itertools
import os
import unittest

from compression import burrows_wheeler
from string_indexing import suffix_array
from string_indexing import fm_index
from generator import rand

class TestFMIndex(unittest.TestCase):
  run_large = unittest.skipUnless(
      os.environ.get('LARGE', False), 'Skip test in small runs')
  
  def get_all_occurences_of_pattern_naive(self, text, n, pattern, l):
    result = []
    for i in range(1, n-l + 2):
      occurs = True
      for j in range(0, l):
        if text[i+j] != pattern[j]:
          occurs = False
          break
      if occurs:
        result.append(i)
    return result
      
  
  def check_fm_api_for_pattern(self, FMIndex, all_occurences_of_pattern, pattern, l):
    cnt = FMIndex.count(pattern, l)
    occurance = FMIndex.get_all_occurrance(pattern, l)
    any_occurance = FMIndex.get_any_occurrance(pattern, l)
    exists = FMIndex.query(pattern, l)
    self.assertEqual(cnt, len(all_occurences_of_pattern))
    self.assertEqual(sorted(occurance), sorted(all_occurences_of_pattern))
    self.assertTrue((any_occurance in all_occurences_of_pattern) or (any_occurance == -1 and len(all_occurences_of_pattern) == 0))
    self.assertTrue(exists == (len(all_occurences_of_pattern) > 0))


  def check_patterns_for_text_naive(self, text, n, patterns):
    SA = suffix_array.naive(text, n)
    BWT = burrows_wheeler.transform_from_suffix_array(SA, text, n)
    FMIndex = fm_index.FMIndex(SA, BWT, text, n)
    for pattern in patterns:
      l = len(pattern)
      pattern_occurances = self.get_all_occurences_of_pattern_naive(text, n, pattern, l)
      self.check_fm_api_for_pattern(FMIndex, pattern_occurances, pattern, l)

  
  api_naive_test_cases = [
    ['#ababa', ['a', 'a', 'aba', 'aa', 'ba', 'ab', 'bb', 'c', 'abc', 'ababa', 'ababaa']],
    ['#aaababcaaabba', ['a', 'b', 'c', 'aab', 'aabb', 'aaababcaaabba']],
    ['#aaabaababaababaababaaababaaabaabaaa', ['a', 'ab', 'aab', 'aaab', 'aaaab', 'aba', 'abaa',
                                              'abaaa', 'aaba', 'aabaa', 'aabaaa', 'aaaba', 'aaabaa']]
  ]
  
  def test_fm_api_naive(self):
    for test_case in self.api_naive_test_cases:
      n = len(test_case[0]) - 1
      self.check_patterns_for_text_naive(test_case[0], n, test_case[1])


  @run_large
  def test_large_random(self):
    n = 10000
    text = '#' + rand.random_word(n, ['a', 'b'])
    q = 1000
    patterns = [rand.random_word(100, ['a', 'b']) for i in range(q)]
    self.check_patterns_for_text_naive(text, n, patterns)


