from compression.core.dictionary import SimpleDict, TrieDict

class LZWSimpleDictParser:
  def __init__(self):
    self.dict = SimpleDict()
    self.counter = 0
    self.temp_phrase = ""
    
  def parse(self, c):
    self.temp_phrase += c
    if self.dict.search(self.temp_phrase) is None:
      self.dict.insert(self.temp_phrase, self.counter)
      self.temp_phrase = c
      self.counter += 1
      return True
    return False

class LZWTrieDictParser:
  def __init__(self, dictionary, dictionary_size):
    self.dict = dictionary
    self.counter = dictionary_size
    self.temp_phrase = self.dict

  def parse(self, c):
    extended = self.temp_phrase.extend(c)
    if extended is None:
      self.temp_phrase.insert(c, self.counter)
      self.temp_phrase = self.dict.search(c)
      self.counter += 1
      #add to reverse trie
      return True
    print('przeszedlem z {0} do {1}'.format(self.temp_phrase.label, extended.label))
    self.temp_phrase = extended
    return False

class GreedyOutputParser:
  def __init__(self, dictionary):
    self.dict = dictionary
    self.temp_phrase = self.dict
    self.output = ""

  def parse(self, c):
    extended = self.temp_phrase.extend(c)
    if extended is None:
      self.output += str(self.temp_phrase.label) + ','
      self.temp_phrase = self.dict.search(c)
      return self.output
    self.temp_phrase = extended
    return ''


class OptimalOutputParser:
  def __init__(self, dictionary):
    self.b = 1
    self.dict = dictionary

  def parse(self, c):
    pass
