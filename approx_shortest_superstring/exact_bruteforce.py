def shortest_common_super(words, alphabet):
  words_batch = ["#"]
  while True:
    next_batch = []
    for c in alphabet:
      for next_word in words_batch:
        if all(word[1:] in next_word for word in words):
          return next_word
        next_batch.append(next_word + c)
    words_batch = next_batch
