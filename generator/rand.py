import random

def random_word(m, A, p = None):
  '''Generates random m-letter word (1-based) with letters in A
  and probabilities p'''
  return '#' + ''.join(letter for letter in random.choices(A, p, k = m))
