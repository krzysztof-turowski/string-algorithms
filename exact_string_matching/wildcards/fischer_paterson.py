def fischer_paterson_match(text, pattern, wildcard='?'):
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
    alphabet = list(alphabet)

    r = n.bit_length()
    mask = (1 << r) - 1

    total_collisions = [0] * (m + n - 1)

    for i in range(len(alphabet)):
        for j in range(len(alphabet)):
            if i != j:
                sigma = alphabet[i]
                tau = alphabet[j]

                x_mask = [1 if c == sigma else 0 for c in text]
                y_mask_rev = [1 if c == tau else 0 for c in reversed(pattern)]

                x_int = 0
                for idx, val in enumerate(x_mask):
                    if val:
                        x_int |= (1 << (idx * r))
                        
                y_int = 0
                for idx, val in enumerate(y_mask_rev):
                    if val:
                        y_int |= (1 << (idx * r))

                z_int = x_int * y_int

                for k in range(m + n - 1):
                    coeff = (z_int >> (k * r)) & mask
                    total_collisions[k] += coeff

    matches = []
    
    for s in range(m - n + 1):
        k = s + n - 1
        
        if total_collisions[k] == 0:
            matches.append(s)

    return matches

if __name__ == "__main__":
    text = "abacbbak?c"
    pattern = "a?a"
    
    results = fischer_paterson_match(text, pattern, wildcard='?')
    
    print(f"Text:    {text}")
    print(f"Pattern: {pattern}")
    print(f"Matched indices: {results}")