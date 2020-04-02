from string_indexing import suffix_tree, suffix_array

# TODO: test suffix_tree

def test_suffix_array(t, n, reference):
  assert suffix_array.naive(t, n) == reference
  assert suffix_array.suffix_array_from_suffix_tree(
      suffix_tree.mccreight(t, n)[0], n) == reference

test_suffix_array("#abaaba", 6, [7, 6, 3, 4, 1, 5, 2])
test_suffix_array("#banana", 6, [7, 6, 4, 2, 1, 5, 3])
