def bitap_shift_add(text: str, word: str, n: int, m: int):
    Sigma = set()
    for c in text[1:]:
        Sigma.add(c)
    for c in word[1:]:
        if c != '?' and c not in Sigma:
            return
    
    ones = (1 << m) - 1

    initval = ones
    for (idx, c) in enumerate(word[1:]):
        if c == '?':
            initval = initval ^ (1 << idx)

    T = {c: initval for c in Sigma}
    for (idx, c) in enumerate(word[1:]):
        if c != '?':
            T[c] = T[c] ^ (1<<idx)

    state = ones

    for (index, c) in enumerate(text):
        if c == '#': continue
        state = state << 1
        state |= T[c]
        if (state & (1<<(m-1)) == 0):
            yield index-m+1
