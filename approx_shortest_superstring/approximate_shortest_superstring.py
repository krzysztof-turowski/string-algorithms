import itertools

def get_all_merges(word1, word2):
  result = []
  for length_of_common_segment in range(0, len(word1)):
    if (word1[len(word1) - length_of_common_segment : ] ==
        word2[1 : 1 + length_of_common_segment]):
      result.append(word1 + word2[1 + length_of_common_segment :])
    if (word2[len(word2) - length_of_common_segment : ] ==
        word1[1 : 1 + length_of_common_segment]):
      result.append(word2 + word1[1 + length_of_common_segment :])
  return result

def get_word_to_merges(words):
  return {(min(word1, word2), max(word1, word2)):\
  get_all_merges(word1, word2) for word1, word2 in\
  itertools.combinations(words, 2)}

def get_merged_to_weight(all_merged_words, word_to_super):
  result = {merged_word : 0 for merged_word in all_merged_words}
  for (word, superstrings) in word_to_super.items():
    for superstring in superstrings:
      result[superstring] += (len(word)-1)

  return result

def update(merged_to_weight, word_to_super,
           word_to_merges, current_words, removed_words):
  for w1 in removed_words:
    for w2 in current_words:
      if w1 == w2:
        continue
      for merged_word in word_to_merges[(min(w1, w2), max(w1, w2))]:
        merged_to_weight.pop(merged_word, None)

  for word in removed_words:
    for superstring_merge in word_to_super[word]:
      if superstring_merge in merged_to_weight:
        merged_to_weight[superstring_merge] -= (len(word)-1)

def shortest_common_super_approx(input_words):
  input_words = list(set(input_words))
  words = [word for word in input_words if all(word == x \
  or word[1:] not in x for x in input_words)]

  while 1:
    word_to_merges = get_word_to_merges(words)

    all_merged_words = [word for merges in \
    word_to_merges.values() for word in merges]

    word_to_super = {word: [merged_word for merged_word in\
    all_merged_words if word[1:] in merged_word] for word in words}

    merged_to_weight = get_merged_to_weight(all_merged_words, word_to_super)

    result = []
    current_words = set(words)
    while len(current_words) > 1:
      merged_candidate = next(iter(merged_to_weight))
      for (merged_word, weight_denominator) in merged_to_weight.items():
        if (len(merged_word) / weight_denominator) <\
        (len(merged_candidate) / merged_to_weight[merged_candidate]):
          merged_candidate = merged_word

      result.append(merged_candidate)

      words_to_remove = [word for word in\
      current_words if word[1:] in merged_candidate]

      update(merged_to_weight, word_to_super,
             word_to_merges, current_words, words_to_remove)

      for word in words_to_remove:
        current_words.remove(word)

    for word in current_words:
      result.append(word)

    if len(result) == 1:
      return result[0]

    words = result
