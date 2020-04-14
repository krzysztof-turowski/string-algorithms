def transform_from_suffix_array(SA, text, n):
  return '#' + ''.join(
      text[SA[i] - 1] if SA[i] > 1 else '$' for i in range(n + 1))

def inverse_transform_naive(BWT):
  raise NotImplementedError
