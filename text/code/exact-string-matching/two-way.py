def two_way(text, word, n, m):
  index, p, use_memory = *critical_factorization(word, m), True
  if index - 1 > m / 2 or not word[index:index + p].endswith(word[1:index]):
    p, use_memory = max(len(word[1:index]), len(word[index:])) + 1, False
  i, memory = 1, 0
  while i <= n - m + 1:
    j = max(index - 1, memory)
    while j < m and text[i + j] == word[j + 1]:
      j = j + 1
    if j < m:
      i, memory = i + j + 2 - index, 0
      continue
    j = max(index - 1, memory)
    while j > memory and text[i + j - 1] == word[j]:
      j = j - 1
    if j == memory:
      yield i
    i, memory = i + p, m - p if use_memory else 0
