# string-algorithms
Collection of algorithms for _String Algorithms_ course (summer semester 2019/20) at [Jagiellonian University](https://uj.edu.pl), [Theoretical Computer Science Department](https://tcs.uj.edu.pl).

## Algorithms

### Exact string matching
1. Morris-Pratt and Knuth-Morris-Pratt algorithms
2. Boyer-Moore algorithm with many variants
3. Boyer-Moore-Apostolico-Giancarlo algorithm
4. Constant space two-way (Crochemore-Perrin) algorithm
5. _fast-on-average_ (Crochemore et al.) algorithm
6. Turbo Boyer-Moore (Crochemore et al.) algorithm
7. Bitap Shift-Add (Baeza-Yates-Gonnet) algorithm
8. Hashing-based (Karp-Rabin) algorithm

### String indexing

#### Suffix tree
1. Weiner algorithm
2. McCreight algorithm
3. Ukkonen on-line algorithm
4. Farach algorithm

#### Suffix array
1. Prefix doubling (Karp-Miller-Rosenberg) algorithm
2. Larsson-Sadakane algorithm
3. Skew (Kärkkäinen-Sanders) algorithm
4. Induced sorting (Zhang-Nong-Chan) algorithm
5. Small-large (Ko-Aluru) algorithm

#### Suffix array search
1. $O(m \log{n})$ naive algorithm
2. Manber-Myers $O(m + \log{n})$ algorithm

#### Longest common prefix
1. Kasai et al. algorithm
2. $\phi$ array-based (Kärkkäinen-Manzini-Puglisi) algorithm
3. Irreducible LCPs-based (Kärkkäinen-Manzini-Puglisi) algorithm

#### Longest previous factor

### Multiple exact string matching
1. Aho-Corasick algorithm
2. Commentz-Walter algorithm
3. _fast-on-average_ (Crochemore et al.) algorithm

### Approximate string matching

#### Longest common subsequence
1. Needleman-Wunsch algorithm
2. Hirschberg algorithm
3. Four Russians (Masek-Paterson) algorithm
4. Myers algorithm
5. Kumar-Rangan algorithm

#### Approximate string matching with Hamming distance
1. Landau-Vishkin algorithm
2. Bitap Shift-Add (Baeza-Yates-Gonnet) algorithm
3. Grossi-Luccio algorithm

#### Approximate string matching with edit distance
1. Approximate Boyer-Moore (Tarhio-Ukkonen) algorithm

#### String matching with wildcards
1. Basic algorithm based on FFT
2. Clifford-Clifford algorithm

#### Approximate string matching with wildcards and Hamming distance
1. Nonrecursive randomised algorithm (Clifford, Eremenko et al.)
2. Recursive randomised algorithm (Clifford, Eremenko et al.)
3. Nonrecursive deterministic algorithm (Clifford, Eremenko et al.)

### Shortest common superstring
1. $\log{n}$-approximation (Li-Jiang) algorithm
2. $4$- and $3$-approximation (Blum et al.) algorithms based on overlaps
3. Greedy overlap algorithm

### Compression

#### Burrows-Wheeler transform

#### Lempel-Ziv 77 factorization

### Other problems
1. Approximate matching of string permutation (Grossi, Luccio)

### Lyndon factorization
1. Maximum suffix algorithm based on prefix-suffix array
2. Maximum suffix algorithm in constant space, based on critical factorization

## Testing

Run all small tests:
```bash
  python3 -B -m unittest discover test -v
```

Run example large test:
```bash
  LARGE=1 python3 -B -m unittest test.test_exact_string_matching.TestExactStringMatching -v
```
