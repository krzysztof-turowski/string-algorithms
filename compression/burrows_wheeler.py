def transform_from_suffix_array(SA, text, n):
  return '#' + ''.join(
      text[SA[i] - 1] if SA[i] > 1 else '$' for i in range(n + 1))

def inverse_transform_naive(BWT, n):
  reversal = [''] * (n + 1)
  for _ in range(n + 1):
    reversal = [c + r for (r, c) in zip(sorted(reversal), BWT[1:])]
  return '#' + ''.join(sorted(reversal)[0][1:])
