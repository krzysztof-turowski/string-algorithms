# string-algorithms
Collection of algorithms for _String Algorithms_ course (summer semesters 2019/20, 2021/22) at [Jagiellonian University](https://uj.edu.pl), [Theoretical Computer Science Department](https://tcs.uj.edu.pl).

## Algorithms

### Text decomposition

#### Maximum suffix
1. Algorithm based on prefix-suffix array
1. Algorithm in constant space, based on critical factorization
1. Adamczyk-Rytter algorithm

#### Lyndon factorization
1. Duval algorithm

### Exact string matching
1. Morris-Pratt and Knuth-Morris-Pratt algorithms
1. Boyer-Moore algorithm with many variants
1. Boyer-Moore-Apostolico-Giancarlo algorithm
1. Galil-Seiferas algorithm
1. Constant space two-way (Crochemore-Perrin) algorithm
1. _fast-on-average_ (Crochemore et al.) algorithm
1. Turbo Boyer-Moore (Crochemore et al.) algorithm
1. Bitap Shift-Add (Baeza-Yates-Gonnet) algorithm
1. Hashing-based (Karp-Rabin) algorithm
1. Crochemore algorithm for ordered alphabets

### String indexing

#### Suffix tree
1. Weiner algorithm
1. McCreight algorithm
1. Ukkonen on-line algorithm
1. Farach algorithm

#### Suffix array
1. Prefix doubling (Karp-Miller-Rosenberg) algorithm
1. Larsson-Sadakane algorithm
1. Skew (Kärkkäinen-Sanders) algorithm
1. Induced sorting (Zhang-Nong-Chan) algorithm
1. Small-large (Ko-Aluru) algorithm

#### Suffix array search
1. $O(m \log{n})$ naive algorithm
1. Manber-Myers $O(m + \log{n})$ algorithm

#### Other index structures
1. FM index (Ferragina-Manzini)
1. LZ index

#### Longest common prefix
1. Kasai et al. algorithm
1. $\phi$ array-based (Kärkkäinen-Manzini-Puglisi) algorithm
1. Irreducible LCPs-based (Kärkkäinen-Manzini-Puglisi) algorithm
1. Wee LCP (Fischer) algorithm

#### Longest previous factor
1. Crochemore-Ilie-Smyth algorithm

### Multiple exact string matching
1. Aho-Corasick algorithm
1. Commentz-Walter algorithm
1. _fast-on-average_ (Crochemore et al.) algorithm

### Approximate string matching

#### Longest common subsequence
1. Needleman-Wunsch algorithm
1. Hirschberg algorithm
1. Four Russians (Masek-Paterson) algorithm
1. Myers algorithm
1. Kumar-Rangan algorithm
1. Hunt-Szymanski algorithm
1. Hunt-Szymanski-Apostolico algorithm

#### Approximate string matching with Hamming distance
1. Landau-Vishkin algorithm
1. Bitap Shift-Add (Baeza-Yates-Gonnet) algorithm
1. Grossi-Luccio algorithm

#### Approximate string matching with edit distance
1. Approximate Boyer-Moore (Tarhio-Ukkonen) algorithm

#### String matching with wildcards
1. Basic algorithm based on FFT
1. Clifford-Clifford algorithm

#### Approximate string matching with wildcards and Hamming distance
1. Nonrecursive randomised algorithm (Clifford, Eremenko et al.)
1. Recursive randomised algorithm (Clifford, Eremenko et al.)
1. Nonrecursive deterministic algorithm (Clifford, Eremenko et al.)

#### Other problems
1. Approximate matching of string permutation algorithm (Grossi-Luccio)

### Shortest common superstring
1. $\log{n}$-approximation (Li-Jiang) algorithm
1. $4$- and $3$-approximation (Blum et al.) algorithms based on overlaps
1. Greedy overlap algorithm
1. Teng-Yao algorithm
1. Paluch-Elbassioni-van Zuylen algorithm

### Compression

#### Burrows-Wheeler transform

#### Lempel-Ziv 77 factorization
1. Crochemore-Ilie-Smyth incomplete factorization algorithm

## Testing

Run all small tests:
```bash
  python -B -m unittest discover test -v
```

Run example large test:
```bash
  LARGE=1 python -B -m unittest test.test_exact_string_matching.TestExactStringMatching -v
```
