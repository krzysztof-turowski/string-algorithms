import collections
import itertools

from common import prefix

def _remove_subwords(words):
  return set(word for word in words
             if all(word == t or word[1:] not in t for t in words))

def exact(T):
  A = set(''.join(T)) - set('#')
  superwords = ['#']
  while True:
    for superword in superwords:
      if all(word[1:] in superword for word in T):
        return superword
    superwords = [superword + c for superword in superwords for c in A]

def naive(T):
  '''Does not change the order of words, only overlaps them'''
  prefixes = [w1[1:-prefix.get_overlap(w1,w2)] if prefix.get_overlap(w1,w2)>0 \
      else w1[1:] for w1,w2 in zip(T,T[1:])]
  return '#' + ''.join(prefixes) + T[-1][1:] if T else ''

def group_merge(T):
  def _get_all_merges(word_1, word_2):
    return [word_1 + word_2[1:], word_2 + word_1[1:]] \
        + [word_1 + word_2[index + 1:] for index in range(1, len(word_1))
           if word_2[1:].startswith(word_1[-index:])] \
        + [word_2 + word_1[index + 1:] for index in range(1, len(word_2))
           if word_1[1:].startswith(word_2[-index:])]

  def _get_word_merges(words):
    return {(word_1, word_2): _get_all_merges(word_1, word_2)
            for word_1, word_2 in itertools.combinations(sorted(words), 2)}

  words = _remove_subwords(T)
  while len(words) > 1:
    word_merges = _get_word_merges(words)
    superstrings = [word for merges in word_merges.values() for word in merges]
    word_to_superstrings = {word: [s for s in superstrings if word[1:] in s]
                            for word in words}

    weights = collections.defaultdict(int)
    for word, superstrings in word_to_superstrings.items():
      for superstring in superstrings:
        weights[superstring] += len(word) - 1

    next_words = set()
    while len(words) > 1:
      candidate = min(weights, key = lambda w: len(w) / weights[w])
      next_words.add(candidate)
      words_to_remove = set(word for word in words if word[1:] in candidate)

      for word_1, word_2 in itertools.product(words_to_remove, words):
        if word_1 == word_2:
          continue
        for word in word_merges[tuple(sorted((word_1, word_2)))]:
          weights.pop(word, None)
      for word in words_to_remove:
        for superstring in word_to_superstrings[word]:
          if superstring in weights:
            weights[superstring] -= len(word) - 1

      words -= words_to_remove
    words |= next_words
  return next(iter(words))

def greedy(T):
  words = _remove_subwords(T)
  while len(words) > 1:
    word_pair = max(itertools.permutations(words, 2),
                    key = lambda p: prefix.get_overlap(*p))
    word_1, word_2, best_overlap = *word_pair, prefix.get_overlap(*word_pair)
    words -= set(word_pair)
    words.add(word_1 + word_2[best_overlap + 1:])
  return '#' + next(iter(words))

def _get_tset(words):
  S, T = _remove_subwords(words), set()
  while S:
    word_pair = max(itertools.product(S, repeat = 2),
                    key = lambda p: prefix.get_overlap(*p))
    word_1, word_2, best_overlap = *word_pair, prefix.get_overlap(*word_pair)
    S.remove(word_1)
    if word_1 != word_2:
      S.remove(word_2)
      S.add(word_1 + word_2[best_overlap + 1:])
    else:
      T.add(word_1)
  return T

def mgreedy(T):
  return '#' + ''.join(t[1:] for t in _get_tset(T))

def tgreedy(T):
  return greedy(_get_tset(T))
