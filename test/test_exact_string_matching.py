from common import prefix, suffix
from exact_string_matching import forward, backward, other

def test_prefix_suffix(t, n, reference):
  assert prefix.prefix_suffix(t, n) == reference
  assert prefix.prefix_suffix_from_strong_prefix_suffix(
      prefix.strong_prefix_suffix(t, n)) == reference

def test_strong_prefix_suffix(t, n, reference):
  assert prefix.strong_prefix_suffix(t, n) == reference

def test_prefix_prefix(t, n, reference):
  assert prefix.prefix_prefix_brute_force(t, n) == reference
  assert prefix.prefix_prefix(t, n) == reference

def test_boyer_moore_shift(t, n, reference):
  assert suffix.boyer_moore_shift_brute_force(t, n) == reference
  assert suffix.boyer_moore_shift(t, n) == reference

def test_get_first_exact_match(t, w, n, m, reference):
  assert next(forward.brute_force(t, w, n, m)) == reference
  assert next(forward.morris_pratt(t, w, n, m)) == reference
  assert next(forward.knuth_morris_pratt(t, w, n, m)) == reference
  assert next(backward.weak_boyer_moore(t, w, n, m)) == reference
  assert next(backward.boyer_moore(t, w, n, m)) == reference
  assert next(backward.boyer_moore_bad_shift(t, w, n, m)) == reference
  assert next(backward.bad_shift_heuristic(t, w, n, m)) == reference
  assert next(backward.quick_search(t, w, n, m)) == reference
  assert next(backward.horspool(t, w, n, m)) == reference
  assert next(backward.boyer_moore_galil(t, w, n, m)) == reference
  assert next(other.fast_on_average(t, w, n, m)) == reference
  # TODO: suffix_tree and suffix_array matching

def test_get_all_exact_matches(t, w, n, m, reference):
  assert list(forward.brute_force(t, w, n, m)) == reference
  assert list(forward.morris_pratt(t, w, n, m)) == reference
  assert list(forward.knuth_morris_pratt(t, w, n, m)) == reference
  assert list(backward.weak_boyer_moore(t, w, n, m)) == reference
  assert list(backward.boyer_moore(t, w, n, m)) == reference
  assert list(backward.boyer_moore_bad_shift(t, w, n, m)) == reference
  assert list(backward.bad_shift_heuristic(t, w, n, m)) == reference
  assert list(backward.quick_search(t, w, n, m)) == reference
  assert list(backward.horspool(t, w, n, m)) == reference
  assert list(backward.boyer_moore_galil(t, w, n, m)) == reference
  assert list(other.fast_on_average(t, w, n, m)) == reference

def test_no_match(t, w, n, m):
  assert not list(forward.brute_force(t, w, n, m))
  assert not list(forward.morris_pratt(t, w, n, m))
  assert not list(forward.knuth_morris_pratt(t, w, n, m))
  assert not list(backward.weak_boyer_moore(t, w, n, m))
  assert not list(backward.boyer_moore(t, w, n, m))
  assert not list(backward.boyer_moore_bad_shift(t, w, n, m))
  assert not list(backward.bad_shift_heuristic(t, w, n, m))
  assert not list(backward.quick_search(t, w, n, m))
  assert not list(backward.horspool(t, w, n, m))
  assert not list(backward.boyer_moore_galil(t, w, n, m))
  assert not list(other.fast_on_average(t, w, n, m))

test_prefix_suffix('#abaab', 5, [-1, 0, 0, 1, 1, 2])
test_prefix_suffix('#abababababb', 11, [-1, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 0])

test_strong_prefix_suffix('#abaab', 5, [-1, 0, -1, 1, 0, 2])
test_strong_prefix_suffix('#abaababa', 8, [-1, 0, -1, 1, 0, -1, 3, -1, 3])

test_prefix_prefix('#abaab', 5, [-1, 5, 0, 1, 2, 0])
test_prefix_prefix('#aabbaaab', 8, [-1, 8, 1, 0, 0, 2, 3, 1, 0])
test_prefix_prefix('#abaa', 4, [-1, 4, 0, 1, 1])
test_prefix_prefix('#aabb', 4, [-1, 4, 1, 0, 0])

test_boyer_moore_shift('#abaaba', 6, [3, 3, 3, 3, 5, 2, 1])

test_get_first_exact_match('#abaaba', '#aab', 6, 3, 3)

test_get_all_exact_matches('#abaaabbaababb', '#abb', 13, 3, [5, 11])

test_no_match('#abaaba', '#baaab', 6, 5)
