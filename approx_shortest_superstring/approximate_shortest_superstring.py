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
  result = {}
  for i, word in enumerate(words):
    for j in range (i+1, len(words)):
      if word < words[j]:
        result[(word, words[j])] = get_all_merges(word, words[j])
      else:
        result[(words[j], word)] = get_all_merges(words[j], word)
  return result

def get_merged_to_weight(all_merged_words, word_to_super):
  result = {merged_word : 0 for merged_word in all_merged_words}
  for (word, superstrings) in word_to_super.items():
    for superstring in superstrings:
      result[superstring] += (len(word)-1)

  return result

def update(merged_to_weight, word_to_super,
           word_to_merges, current_words, removed_words):
  for word1 in removed_words:
    for word2 in current_words:
      if word1 < word2:
        for merged_word in word_to_merges[(word1, word2)]:
          merged_to_weight.pop(merged_word, None)
      elif word1 > word2:
        for merged_word in word_to_merges[(word2, word1)]:
          merged_to_weight.pop(merged_word, None)

  for word in removed_words:
    for superstring_merge in word_to_super[word]:
      if superstring_merge in merged_to_weight:
        merged_to_weight[superstring_merge] -= (len(word)-1)

def shortest_common_super_approx(words):
  words = list(set(words))
  words = list(filter(lambda word: all(word == x \
  or word[1:] not in x for x in words), words))

  word_to_merges = get_word_to_merges(words)

  all_merged_words = [word for merges in \
  word_to_merges.values() for word in merges]

  word_to_super = {word: list(filter(lambda merge_word : word[1:] in \
  merge_word, all_merged_words)) for word in words}

  merged_to_weight = get_merged_to_weight(all_merged_words, word_to_super)

  result = []
  current_words = set(words)
  while len(current_words) > 1:
    merged_candidate = None
    candidate_weight = 1e9
    for (merged_word, weight_denominator) in merged_to_weight.items():
      if (len(merged_word) / weight_denominator) < candidate_weight:
        merged_candidate = merged_word

    result.append(merged_candidate)

    words_to_remove = list(filter(lambda word: word[1:] in\
    merged_candidate, current_words))

    update(merged_to_weight, word_to_super,
           word_to_merges, current_words, words_to_remove)

    for word in words_to_remove:
      current_words.remove(word)

  for word in current_words:
    result.append(word)

  if len(result) == 1:
    return result[0]

  return shortest_common_super_approx(result)
