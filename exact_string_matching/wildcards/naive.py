def naive_match(text, pattern, wildcard='?'):
    """
    Finds all occurrences of a pattern in a text using the naive (brute-force) approach.
    Supports wildcard symbols (don't cares) in both the text and the pattern.
    
    Time Complexity: O(n * m) in the worst case.
    Space Complexity: O(1) auxiliary space.
    """
    n = len(text)
    m = len(pattern)
    matches = []

    # Edge cases
    if m == 0 or n < m:
        return matches

    # iterate over all possible starting shifts in the text
    for i in range(n - m + 1):
        match_found = True
        
        # Verify character by character for the current shift
        for j in range(m):
            t_char = text[i + j]
            p_char = pattern[j]
            
            if t_char != p_char and t_char != wildcard and p_char != wildcard:
                match_found = False
                break 
                
        if match_found:
            matches.append(i)
            
    return matches

if __name__ == "__main__":
    text_data = "a?acbb?ac"
    pattern_data = "a?a"
    
    results = naive_match(text_data, pattern_data, wildcard='?')
    
    print(f"Text:    {text_data}")
    print(f"Pattern: {pattern_data} ('?' is the wildcard)")
    print(f"Matches found at indices: {results}")