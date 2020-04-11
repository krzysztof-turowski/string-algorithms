# string-algorithms
Collection of algorithms for _String Algorithms_ course (summer semester 2019/20) at [Jagiellonian University](https://uj.edu.pl), [Theoretical Computer Science Department](https://tcs.uj.edu.pl).

## Algorithms

### Exact string matching
1. Morris-Pratt and Knuth-Morris-Pratt algorithms
2. Boyer-Moore algorithm with many variants
3. _fast-on-average_ algorithm

### String indexing
1. Suffix tree: Weiner, McCreight and Ukkonen algorithms
2. Suffix array: Karp-Miller-Rosenberg and Kärkkäinen-Sanders algorithms

## Testing

Run all tests:
```bash
  python3 -B -m unittest discover test -v
```

Run example large test:
```bash
  LARGE=1 python3 -B -m unittest test.test_exact_string_matching.TestExactStringMatching.test_random_exact_string_matching -v
```
