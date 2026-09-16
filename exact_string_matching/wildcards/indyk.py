import numpy as np
import math
import random

def indyk_randomized_match(text, pattern, wildcard='?', c=7):
    """
    Finds all occurrences of a pattern in a text using Indyk's randomized Monte Carlo algorithm.
    
    This probabilistic algorithm decouples the execution time from the alphabet size, 
    achieving an optimal O(n log n) complexity. It maps standard characters to random 
    boolean values across d independent dimensions (where d = c * log2(n)). To safely 
    neutralize wildcards, they are explicitly projected to zero in all dimensions.
    
    The algorithm performs d independent frequency-domain convolutions. In each pass, 
    mismatches between different characters have a high probability of generating 
    arithmetic collisions. By accumulating the results across all d projections, 
    the probability of a false positive exponentially decreases. A shift is considered 
    a valid match if and only if zero collisions are registered across all dimensions.
    
    Args:
        text (str): The main text to be searched.
        pattern (str): The pattern containing potential wildcard symbols.
        wildcard (str): The character used as the 'don't care' symbol (default: '?').
        c (int): The confidence constant determining the number of iterations (default: 7).
        
    Returns:
        list: A list of starting indices in the text where the pattern matches.
    """
    n = len(text)
    m = len(pattern)
    
    if m == 0 or n < m:
        return []

    alphabet = set(text) | set(pattern)
    if wildcard in alphabet:
        alphabet.remove(wildcard)
    alphabet = list(alphabet)
    
    d = int(math.ceil(c * math.log2(n if n > 1 else 2)))
    
    r = {char: [random.randint(0, 1) for _ in range(d)] for char in alphabet}
    
    def f(char, k):
        return r[char][k] if char != wildcard else 0
        
    def g(char, k):
        return (1 - r[char][k]) if char != wildcard else 0

    L = 1
    while L < n + m - 1:
        L <<= 1

    total_collisions = np.zeros(L)
    
    for k in range(d):
        T_mask = np.array([g(char, k) for char in text], dtype=float)
        
        P_mask = np.array([f(char, k) for char in pattern], dtype=float)
        P_mask_rev = P_mask[::-1]
        
        T_f = np.fft.fft(T_mask, L)
        P_f = np.fft.fft(P_mask_rev, L)
        
        conv_result = np.fft.ifft(T_f * P_f).real
        
        total_collisions += np.round(conv_result)
        
    matches = []
    
    for s in range(n - m + 1):
        if total_collisions[s + m - 1] == 0:
            matches.append(s)
            
    return matches

if __name__ == "__main__":
    text = "abacbbak?c"
    pattern = "a?a"
    
    results = indyk_randomized_match(text, pattern, wildcard='?', c=7)
    
    print(f"Text:    {text}")
    print(f"Pattern: {pattern}")
    print(f"Matched indices: {results}")