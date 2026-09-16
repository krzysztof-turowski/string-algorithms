import numpy as np
import random

def kalai_fingerprint_match(text, pattern, wildcard='?'):
    """
    Finds pattern matches in a text using Kalai's randomized fingerprinting algorithm.
    
    This probabilistic approach efficiently handles wildcards in both the text and 
    the pattern. It assigns random weights to pattern characters (with wildcards 
    weighing 0) to create a unique mathematical fingerprint. 
    
    Using just two parallel FFT convolutions, it calculates a sliding text fingerprint (S) 
    and a dynamic target fingerprint (T). A match occurs wherever S and T are equal. 
    This method guarantees a low false-positive rate while remaining memory-efficient 
    and completely independent of the alphabet size.
    
    Args:
        text (str): The main text to be searched (can contain wildcards).
        pattern (str): The pattern sequence (can contain wildcards).
        wildcard (str): The character used as the 'don't care' symbol (default: '?').
        
    Returns:
        list: A list of starting indices in the text where the pattern matches.
    """
    n = len(text)
    m = len(pattern)
    
    if m == 0 or n < m:
        return []

    N = max(n**2, 1000)
    
    R = np.zeros(m)
    Y_num = np.zeros(m)
    for i, char in enumerate(pattern):
        if char == wildcard:
            R[i] = 0
            Y_num[i] = 0
        else:
            R[i] = random.randint(1, N)
            Y_num[i] = ord(char)
            
    R_rev = R[::-1]
    YR_rev = (Y_num * R)[::-1]

    X_num = np.array([0 if c == wildcard else ord(c) for c in text], dtype=float)
    X_ind = np.array([0 if c == wildcard else 1 for c in text], dtype=float)

    L = 1
    while L < n + m - 1:
        L <<= 1

    X_num_f = np.fft.fft(X_num, L)
    R_rev_f = np.fft.fft(R_rev, L)
    S = np.fft.ifft(X_num_f * R_rev_f).real

    X_ind_f = np.fft.fft(X_ind, L)
    YR_rev_f = np.fft.fft(YR_rev, L)
    T = np.fft.ifft(X_ind_f * YR_rev_f).real

    matches = []
    
    for j in range(n - m + 1):
        k = j + m - 1
        
        if abs(S[k] - T[k]) < 0.5:
            matches.append(j)

    return matches

if __name__ == "__main__":
    text = "abacbbak?c"
    pattern = "a?a"
    
    results = kalai_fingerprint_match(text, pattern, wildcard='?')
    
    print(f"Text:    {text}")
    print(f"Pattern: {pattern}")
    print(f"Matched indices: {results}")