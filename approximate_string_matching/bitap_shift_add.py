from math import ceil, log2


def bitap_shift_add(text: str, word: str, _n: int, m: int, k: int):
    # the alphabet we're working on
    Sigma = set()
    for c in text[1:]:
        Sigma.add(c)

    # number of bits required for each
    # position in the pattern
    B = ceil(log2(k+1)) + 1

    # bitmask of (m*B) ones for trimming
    # the state and overflow to length
    ones = (1 << (m*B)) - 1
    
    # the initial value for the state
    # as well as calculating the lookup
    initval = 0
    for _ in range(m):
        initval = initval << B
        initval |= 1

    # overflow mask for clearing and
    # recording the overflow bits
    mask = 0
    for _ in range(m):
        mask = mask << B
        mask |= 1 << (B-1)

    # lookup for each character
    # T[c] has 0 at i-th position iff word[i] == c
    # and 1 otherwise.
    # We ignore characters not in text
    # since we'll never look them up
    T = {c: initval for c in Sigma}
    for (idx, c) in enumerate(word[1:]):
        if c in Sigma:
            T[c] = T[c] ^ (1<<(idx*B))

    # the state (mismatches up to the i-th position)
    state = initval
    # overflow set, for recording
    # when the number of mismatches
    # exceeded `k` in the state
    overflow = mask

    for (index, c) in enumerate(text):
        if c == '#': continue

        # shift-add operation
        state = (state << B) + T[c]
        state &= ones

        # record overflow bits
        overflow = (overflow << B) | (state & mask)
        overflow &= ones

        # clear the overflow bits from state
        state &= ~mask

        # return a match when the number of mismatches
        # up to the m-the position (i.e. the whole pattern)
        # is at most than k (that is, state at m-th position
        # is less than k+1 and overflow isn't set)
        if (state | overflow) < ((k+1) << (m-1)*B):
            yield index-m+1
