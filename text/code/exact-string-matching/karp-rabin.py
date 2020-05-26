def karp_rabin(text, word, n, m):
  MOD = 257
  A = random.randint(2, MOD - 1)
  Am = pow(A, m, MOD)
  def generate(t):
    return sum(ord(c) * pow(A, i, MOD) for i, c in enumerate(t[::-1])) % MOD
  text += '$'
  hash_text, hash_word = generate(text[1:m + 1]), generate(word[1:])
  for i in range(1, n - m + 2):
    if hash_text == hash_word and text[i:i + m] == word[1:]:
      yield i
    hash_text = (A * hash_text + ord(text[i + m]) - Am * ord(text[i])) % MOD
