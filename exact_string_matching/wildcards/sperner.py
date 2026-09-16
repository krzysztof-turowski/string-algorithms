import numpy as np
import math
from itertools import combinations

def sperner_wildcard_match(text, pattern, wildcard='?'):
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
    
    Args:
        text (str): The main text to be searched.
        pattern (str): The pattern sequence containing potential wildcard symbols.
        wildcard (str): The character used as the 'don't care' symbol (default: '?').
        
    Returns:
        list: A list of starting indices in the text where the pattern matches.
    """
    m = len(text)
    n = len(pattern)
    
    if n == 0 or m < n:
        return []

    alphabet = set(text) | set(pattern)
    alphabet.discard(wildcard)
    alphabet = list(alphabet)
    num_symbols = len(alphabet)

    if num_symbols == 0:
        return list(range(m - n + 1))

    k = 1
    while math.comb(k, k // 2) < num_symbols:
        k += 1

    subsets = list(combinations(range(k), k // 2))
    char_to_subset = {alphabet[i]: set(subsets[i]) for i in range(num_symbols)}

    L = 1
    while L < m + n - 1:
        L <<= 1

    total_collisions = np.zeros(L)

    for i in range(k):
        T_mask = np.zeros(m)
        for idx, c in enumerate(text):
            if c != wildcard and i in char_to_subset[c]:
                T_mask[idx] = 1

        P_mask = np.zeros(n)
        for idx, c in enumerate(pattern):
            if c != wildcard and i not in char_to_subset[c]:
                P_mask[idx] = 1

        T_f = np.fft.fft(T_mask, L)
        P_f = np.fft.fft(P_mask[::-1], L)
        
        conv_result = np.fft.ifft(T_f * P_f).real
        total_collisions += np.round(conv_result)

    matches = []
    
    for s in range(m - n + 1):
        if total_collisions[s + n - 1] == 0:
            matches.append(s)

    return matches

if __name__ == "__main__":
    text = "abacbbak?c"
    pattern = "a?a"
    
    results = sperner_wildcard_match(text, pattern, wildcard='?')
    
    print(f"Text:    {text}")
    print(f"Pattern: {pattern}")
    print(f"Matched indices: {results}")