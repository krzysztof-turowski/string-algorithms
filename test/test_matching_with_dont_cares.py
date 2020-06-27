import unittest

from approximate_string_matching.matching_with_dont_cares \
  import exact_matching_with_dont_cares

class ExactMatchingWithDontCaresCase(unittest.TestCase):
  def make_test(self, text, pattern, result):
    matches = exact_matching_with_dont_cares(text, pattern,
                                             len(text),
                                             len(pattern))
    self.assertEqual(result, list(matches))

  def test_given_input_with_no_wildcards_returns_matches(self):
    self.make_test('#abbabaaa', '#ab', [1, 4])

  def test_given_input_with_wildcards_returns_matches(self):
    self.make_test('#abbabaaa', '#??a', [2, 4, 5, 6])

  def test_simple(self):
    self.make_test('#aa', '#a', [1, 2])
