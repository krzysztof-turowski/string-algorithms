from generator import rand
from common import suffix
from exact_string_matching import forward, backward, other

ALGORITHMS = [
    forward.morris_pratt,
    forward.knuth_morris_pratt,
    backward.boyer_moore,
    backward.boyer_moore_bad_shift,
    backward.bad_shift_heuristic,
    backward.boyer_moore_galil,
    backward.quick_search,
    backward.horspool,
    other.fast_on_average,
]

def random_exact_string_matching_test(n, m, A):
  t, w = rand.random_word(n, A), rand.random_word(m, A)
  reference_result = list(forward.brute_force(t, w, n, m))
  for algorithm in ALGORITHMS:
    result = list(algorithm(t, w, n, m))
    assert result == reference_result

def random_boyer_moore_shift_test(m, A):
  w = rand.random_word(m, A)
  assert suffix.boyer_moore_shift_brute_force(w, m) == suffix.boyer_moore_shift(w, m)

for _ in range(200):
  random_exact_string_matching_test(3000, 50, ['a', 'b'])
for _ in range(200):
  random_boyer_moore_shift_test(3000, ['a', 'b'])
