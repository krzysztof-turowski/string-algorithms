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
  def __init__(self, dictionary, reverse_dictionary, dictionary_size):
    self.dict = dictionary
    self.rev_dict = reverse_dictionary
    self.counter = dictionary_size
    self.temp_phrase = self.dict
    self.temp_phrase_str = ""

  def parse(self, c):
    extended = self.temp_phrase.extend(c)
    if extended is None:
      node = self.temp_phrase.insert(c, self.counter)
      #add to reverse trie
      rev_node = self.rev_dict.insert(str(self.temp_phrase_str + c)[::-1], self.counter)
      node.connect(rev_node)
      rev_node.connect(node)
      self.temp_phrase = self.dict.search(c)
      self.temp_phrase_str = c
      self.counter += 1
      return node
    print('przeszedlem z {0} do {1}'.format(self.temp_phrase.label, extended.label))
    self.temp_phrase = extended
    self.temp_phrase_str += c
    return None

class LZ78TrieDictParser:
  def __init__(self, dictionary, reverse_dictionary, dictionary_size):
    self.dict = dictionary
    self.rev_dict = reverse_dictionary
    self.counter = dictionary_size + 1
    self.temp_phrase = self.dict
    self.temp_phrase_str = ""

  def parse(self, c):
    extended = self.temp_phrase.extend(c)
    if extended is None:
      print('dodaje', self.temp_phrase.index, c)
      node = self.temp_phrase.insert(c, (self.temp_phrase.index, c, self.counter), self.counter)
      #add to reverse trie
      rev_node = self.rev_dict.insert(str(self.temp_phrase_str + c)[::-1], (self.temp_phrase.index, c, self.counter), self.counter)
      node.connect(rev_node)
      rev_node.connect(node)
      self.counter += 1
      self.temp_phrase = self.dict#.search(c)
      self.temp_phrase_str = ""
      return node
    print('przeszedlem z {0} do {1}'.format(self.temp_phrase.label, extended.label))
    self.temp_phrase = extended
    self.temp_phrase_str += c
    return None

class GreedyOutputParser:
  def __init__(self, dictionary, reverse_dictionary):
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

  def parse_end(self):
    self.parse('')


class OptimalOutputParser:
  def __init__(self, dictionary, reverse_dictionary):
    self.dict = dictionary
    self.rev_dict = reverse_dictionary
    self.b = 1
    self.fb = 1
    self.offset = 0
    self.temp_phrase = self.dict
    self.output = ""
    self.tmp_out = ""
    
  def parse(self, c):
    self.tmp_out += c
    extended = self.temp_phrase.extend(c)
    if extended is None:
      # we know new value of some suffix of T[b:]
      # w obu case'ach i tak robie cos takiego, ze biore nadluzszy sufiks tego co mam < fb
      # robie while dopoki nie mam tak, ze znajde suf ktory c rozszerzy i bedzie < fb
      tmp_offset = 0
      tmp_depth = self.temp_phrase.depth
      while True:
        longest_suffix = self.temp_phrase.contract()
        print('long suf', longest_suffix.label)
        tmp_offset += self.temp_phrase.depth - longest_suffix.depth
       
        # jak znajde to sprawdzam czy rozszerze go o c
        extended = longest_suffix.extend(c)
        # jak nie to szukam innego sufiksu (to ma stop bo jednoliterowce sa ok)
        if extended is None:
          self.temp_phrase = longest_suffix
          # if self.temp_phrase.label == '$'
          continue
        # jak tak to next iteracja
        else:
          print('uff rozszerzylem', extended.label)
          self.temp_phrase = extended
          break
      
      print('el', extended.label, tmp_offset)
      print('jestem w', self.b, self.fb, 'z offsetem', self.offset, 'i zjadlem kolejne', tmp_offset)
      # jak nie znajde to output... tylko co?
      if self.b + self.offset + tmp_offset > self.fb + 1:
        # ???
        # todo proper prefix   
        # 
        tmp_node = self.dict.search(self.tmp_out[0:self.offset])       
        self.output += str(tmp_node.label) + ','
        self.tmp_out = self.tmp_out[self.offset:]

        self.b += self.offset
        self.fb = self.b + tmp_depth - 1
        self.offset = tmp_offset
        # self.temp_phrase = self.dict.search(c)
        return self.output
      else:
        self.offset += tmp_offset
        return ''

    print('el2', extended.label)
    self.temp_phrase = extended
    return ''

  def parse_end(self):
    print('pe', self.tmp_out, self.offset, self.tmp_out[0:self.offset])
    if self.offset > 0:
      tmp_node = self.dict.search(self.tmp_out[0:self.offset])       
      self.output += str(tmp_node.label) + ','
      self.tmp_out = self.tmp_out[self.offset:]
    if self.tmp_out:
      tmp_node = self.dict.search(self.tmp_out)   
      self.output += str(tmp_node.label) + ','
    # print(self.b, self.fb, self.offset, self.tmp_out)
    return self.output
