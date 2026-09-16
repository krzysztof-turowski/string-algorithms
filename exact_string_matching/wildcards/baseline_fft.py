import numpy as np

def baseline_fft_match(text, pattern, wildcard='?'):
    """
    Finds all occurrences of a pattern in a text using the Baseline Character-Masked FFT algorithm.
    
    This method loops through every unique character found in the text and pattern. 
    For each character, it creates two binary masks: one for the text (marking where 
    the character appears) and one for the reversed pattern (marking where a different, 
    non-wildcard character appears). 
    
    By multiplying these masks using the Fast Fourier Transform (FFT), 
    the algorithm quickly counts the exact number of character collisions for all possible 
    shifts. After checking all characters in the alphabet, any shift that has 0 total 
    collisions is considered a valid match.
    
    Args:
        text (str): The main text to be searched.
        pattern (str): The pattern containing potential wildcard symbols.
        wildcard (str): The character used as the 'don't care' symbol (default: '?').
        
    Returns:
        list: A list of starting indices in the text where the pattern matches.
    """
    m = len(text)
    n = len(pattern)
    
    if n == 0 or m < n:
        return []

    alphabet = set(text) | set(pattern)
    if wildcard in alphabet:
        alphabet.remove(wildcard)

    L = 1
    while L < m + n - 1:
        L <<= 1

    total_mismatches = np.zeros(L, dtype=complex)
    reversed_pattern = pattern[::-1]

    for sigma in alphabet:
        U = np.array([1.0 if c == sigma else 0.0 for c in text])
        V = np.array([1.0 if (c != sigma and c != wildcard) else 0.0 for c in reversed_pattern])

        U_padded = np.pad(U, (0, L - len(U)))
        V_padded = np.pad(V, (0, L - len(V)))

        U_fft = np.fft.fft(U_padded)
        V_fft = np.fft.fft(V_padded)
        
        total_mismatches += np.fft.ifft(U_fft * V_fft)

    matches = []
    
    for s in range(m - n + 1):
        val = total_mismatches[s + n - 1].real
        
        if val < 0.5:
            matches.append(s)

    return matches

if __name__ == "__main__":
    text = "abacbbak?c"
    pattern = "a?a"
    
    results = baseline_fft_match(text, pattern, wildcard='?')
    
    print(f"Text:    {text}")
    print(f"Pattern: {pattern}")
    print(f"Matched indices: {results}")