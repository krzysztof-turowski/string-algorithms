# pylint: disable=too-few-public-methods
class DictParser(object):
  def __init__(self, dictionary, label_extractor, extension_callback):
    self.dict = dictionary
    self.phrase = self.dict.trie
    self.label_extractor = label_extractor
    self.extension_callback = extension_callback

  def parse(self, c):
    extended = self.phrase.extend(c)
    if extended is None:
      reversed_phrase = str(self.dict.get_prefix(self.phrase) + c)[::-1]
      node = self.dict.insert(
          self.phrase, c, reversed_phrase, self.label_extractor(self, c)
      )
      self.phrase = self.extension_callback(self, c)
      return node
    self.phrase = extended
    return None

class OutputParser(object):
  def __init__(self, dictionary):
    self.dict = dictionary
    self.phrase = self.dict.trie

  def parse(self, c):
    raise NotImplementedError

  def parse_end(self):
    raise NotImplementedError

class GreedyOutputParser(OutputParser):
  def parse(self, c):
    extended = self.phrase.extend(c)
    if extended is None:
      code = str(self.phrase.label) if self.phrase.label is not None else None
      self.phrase = self.dict.search(c)
      return code
    self.phrase = extended
    return None

  def parse_end(self):
    code = self.parse('')
    return [code] if code is not None else []

class OptimalOutputParser(OutputParser):
  def __init__(self, dictionary):
    super(OptimalOutputParser, self).__init__(dictionary)
    self.beginning = 1
    self.f_beginning = 1
    self.offset = 0
    self.tmp_out = ""

  def parse(self, c):
    self.tmp_out += c
    extended = self.phrase.extend(c)
    if extended is None:
      tmp_offset = 0
      tmp_depth = self.phrase.depth
      while True:
        longest_suffix = self.phrase.contract()
        tmp_offset += self.phrase.depth - longest_suffix.depth
        extended = longest_suffix.extend(c)
        if extended is None:
          self.phrase = longest_suffix
          continue
        else:
          self.phrase = extended
          break

      if self.beginning + self.offset + tmp_offset > self.f_beginning + 1:
        tmp_node = self.dict.search(self.tmp_out[0:self.offset])
        code = str(tmp_node.label)
        self.tmp_out = self.tmp_out[self.offset:]

        self.beginning += self.offset
        self.f_beginning = self.beginning + tmp_depth - 1
        self.offset = tmp_offset
        return code

      self.offset += tmp_offset
      return None

    self.phrase = extended
    return None

  def parse_end(self):
    code = []
    if self.offset > 0:
      tmp_node = self.dict.search(self.tmp_out[0:self.offset])
      code.append(str(tmp_node.label))
      self.tmp_out = self.tmp_out[self.offset:]
    if self.tmp_out:
      tmp_node = self.dict.search(self.tmp_out)
      code.append(str(tmp_node.label))
    return code
