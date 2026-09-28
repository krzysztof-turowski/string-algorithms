import itertools
import math
import scipy.signal
import numpy as np
import random

def basic_fft(text, word, n, m):
  if n < m:
    return
  A = set(list(text[1:] + word[1:])) - set('?')
  mismatches = [0] * (n - m + 1)
  for first_letter in A:
    masked_text = [int(c == first_letter) for c in text[1:]]
    for second_letter in A:
      if first_letter != second_letter:
        masked_word = [int(c == second_letter) for c in reversed(word[1:])]
        mismatches_ab = scipy.signal.convolve(
            masked_text, masked_word, mode = 'valid', method = 'fft')
        mismatches = [x + y for x, y in zip(mismatches, mismatches_ab)]
  yield from (index + 1 for index, is_mismatch in enumerate(mismatches)
              if is_mismatch == 0)

def clifford_clifford_parts(text, word, n, m):
  def _compute_part(index, part):
    return [index * m + i
            for i in clifford_clifford(part, word, len(part) - 1, m)]

  if n < m:
    return
  parts = ['#' + text[i * m + 1:(i + 2) * m + 1]
           for i in range(math.ceil(n / m))]
  results = (_compute_part(index, part) for index, part in enumerate(parts))
  yield from sorted(set(index for result in results for index in result))

def clifford_clifford(text, word, n, m):
  def _times(x, y):
    return list(itertools.starmap(lambda a, b: a * b, zip(x, y)))

  if n < m:
    return
  A = set(list(text[1:] + word[1:])) - set('?')
  letter_mapping = {c: i for i, c in enumerate(A, start = 1)}
  letter_mapping.update({'?': 0})
  text = [letter_mapping.get(c) for c in text[1:]]
  word = [letter_mapping.get(c) for c in word[:0:-1]]

  first_component = scipy.signal.convolve(
      _times(word, _times(word, word)), text, mode = 'valid', method = 'fft')
  second_component = scipy.signal.convolve(
      _times(word, word), _times(text, text), mode = 'valid', method = 'fft')
  third_component = scipy.signal.convolve(
      word, _times(text, _times(text, text)), mode = 'valid', method = 'fft')
  result = [first - 2 * second + third for first, second, third in
            zip(first_component, second_component, third_component)]
  yield from (index + 1 for index, value in enumerate(result) if value == 0)

def naive(text, word, n, m):
    """
    Finds all occurrences of a pattern in a text using the naive (brute-force) approach.
    Supports wildcard symbols (don't cares) in both the text and the pattern.
    
    Time Complexity: O(n * m) in the worst case.
    Space Complexity: O(1) auxiliary space.
    """
    if m == 0 or n < m:
        return

    text_string, word_string = text[1:], word[1:]

    for i in range(n - m + 1):
        if all(text_string[i + j] == word_string[j] or text_string[i + j] == '?' or word_string[j] == '?' for j in range(m)):
            yield i + 1

def fischer_paterson(text, word, n, m):
    """
    Finds all occurrences of a pattern in a text using the Fischer-Paterson bitwise algorithm.
    
    Instead of checking characters one by one, this algorithm finds mismatches by packing 
    the text and pattern into massive integers. For every pair of different characters in 
    the alphabet, it creates binary masks (1 where the character exists, 0 elsewhere). 
    These masks are shifted and packed into large integers. 
    
    By multiplying these numbers together, the algorithm calculates all character 
    collisions for every possible shift at once. A buffer constant is used to safely 
    space the values apart and prevent bits from overlapping. If the total number of 
    collisions at a specific shift equals zero, it means the pattern perfectly 
    matches the text at that position.
    """
    if m == 0 or n < m:
        return

    text_string, word_string = text[1:], word[1:]

    alphabet = set(text_string) | set(word_string)
    alphabet.discard('?')
    alphabet = list(alphabet)

    buffer_bit_length = m.bit_length()
    mask = (1 << buffer_bit_length) - 1

    total_collisions = [0] * (n + m - 1)

    for sigma, tau in itertools.permutations(alphabet, 2):
        
        x_mask = [1 if c == sigma else 0 for c in text_string]
        y_mask_reverse = [1 if c == tau else 0 for c in reversed(word_string)]

        x_int = sum(1 << (index * buffer_bit_length) for index, value in enumerate(x_mask) if value)
        y_int = sum(1 << (index * buffer_bit_length) for index, value in enumerate(y_mask_reverse) if value)

        z_int = x_int * y_int

        for k in range(n + m - 1):
            coefficient = (z_int >> (k * buffer_bit_length)) & mask
            total_collisions[k] += coefficient
            
    yield from (s + 1 for s in range(n - m + 1) if total_collisions[s + m - 1] == 0)

def indyk(text, word, n, m, c=7):
    """
    Finds all occurrences of a pattern in a text using Indyk's randomized Monte Carlo algorithm.
    
    This algorithm decouples the execution time from the alphabet size by mapping standard characters
    to random boolean values across d independent dimensions (where d = O(log n)), while explicitly
    projecting wildcards to zero. It then performs d independent frequency-domain convolutions,
    where character mismatches have a high probability of generating arithmetic collisions. By 
    accumulating these results across all projections, the probability of a false positive decreases 
    exponentially, and a shift is a valid match if and only if zero collisions are registered.

    Note on Complexity: 
    For benchmarking consistency with other algorithms in this repository, this implementation 
    uses standard FFT (`scipy.signal.convolve`) instead of polynomial multiplication over GF(2). 
    This results in a practical time complexity of O(n log^2 n) rather than the theoretical O(n log n).
    """
    if m == 0 or n < m:
        return

    text_string, word_string = text[1:], word[1:]

    alphabet = set(text_string) | set(word_string)
    alphabet.discard('?')
    alphabet = list(alphabet)
    
    d = int(math.ceil(c * math.log2(n if n > 1 else 2)))
    random_projections = {char: [random.randint(0, 1) for _ in range(d)] for char in alphabet}
    
    def f(char, k):
        return random_projections[char][k] if char != '?' else 0
        
    def g(char, k):
        return (1 - random_projections[char][k]) if char != '?' else 0

    total_collisions = np.zeros(n - m + 1)
    
    for k in range(d):
        text_mask = [g(char, k) for char in text_string]
        word_mask_reverse = [f(char, k) for char in reversed(word_string)]
        
        convolution_result = scipy.signal.convolve(text_mask, word_mask_reverse, mode='valid', method='fft')
        total_collisions += np.round(convolution_result.real)
        
    yield from (s + 1 for s, value in enumerate(total_collisions) if value == 0)

def sperner(text, word, n, m):
    """
    Finds pattern matches in a text using Sperner's optimization and conflict graph reduction.
    
    This algorithm reduces the alphabet size dependency by leveraging Sperner's theorem. 
    It computes a minimal universe size (k) such that the binomial coefficient (k choose k//2) 
    is at least equal to the alphabet size. Each character is then assigned a unique subset 
    of size k//2. 
    
    By executing k parallel convolutions using FFT, the algorithm checks for character 
    conflicts across independent dimensions. Wildcards are explicitly ignored. 
    A match is confirmed at a specific shift if zero total collisions are recorded across 
    all k passes.
    """
    if m == 0 or n < m:
        return

    text_string, word_string = text[1:], word[1:]

    alphabet = set(text_string) | set(word_string)
    alphabet.discard('?')
    alphabet = list(alphabet)
    num_symbols = len(alphabet)

    if num_symbols == 0:
        yield from range(1, n - m + 2)
        return

    k = 1
    while math.comb(k, k // 2) < num_symbols:
        k += 1

    char_to_subset = {char: set(subset) for char, subset in zip(alphabet, itertools.combinations(range(k), k // 2))}

    total_collisions = np.zeros(n - m + 1)

    for i in range(k):
        text_mask = [1 if c != '?' and i in char_to_subset[c] else 0 for c in text_string]
        word_mask_reverse = [1 if c != '?' and i not in char_to_subset[c] else 0 for c in reversed(word_string)]

        convolution_result = scipy.signal.convolve(text_mask, word_mask_reverse, mode='valid', method='fft')
        total_collisions += np.round(convolution_result.real)

    yield from (s + 1 for s, value in enumerate(total_collisions) if value == 0)

def kalai(text, word, n, m):
    """
    Finds pattern matches in a text using Kalai's randomized fingerprinting algorithm.
    
    This probabilistic approach efficiently handles wildcards in both the text and 
    the pattern. It assigns random weights to pattern characters (with wildcards 
    weighing 0) to create a unique mathematical fingerprint. 
    
    Using just two parallel FFT convolutions, it calculates a sliding text fingerprint (S) 
    and a dynamic target fingerprint (T). A match occurs wherever S and T are equal. 
    This method guarantees a low false-positive rate while remaining memory-efficient 
    and completely independent of the alphabet size.
    """
    if m == 0 or n < m:
        return

    text_string, word_string = text[1:], word[1:]

    N = n**2 + 1
    
    r_array = [0 if c == '?' else random.randint(1, N) for c in word_string]
    y_values = [0 if c == '?' else ord(c) for c in word_string]
    
    r_reverse = r_array[::-1]
    yr_reverse = [y * r for y, r in zip(y_values, r_array)][::-1]

    x_values = [0 if c == '?' else ord(c) for c in text_string]
    x_indicator = [0 if c == '?' else 1 for c in text_string]

    S = scipy.signal.convolve(x_values, r_reverse, mode='valid', method='fft')
    T = scipy.signal.convolve(x_indicator, yr_reverse, mode='valid', method='fft')

    yield from (j + 1 for j, (s_value, t_value) in enumerate(zip(S, T)) if round(s_value.real - t_value.real) == 0)