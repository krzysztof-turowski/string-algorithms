class Compressor:
  def __init__(self, dictionary, parser_dictionary, parser_output):
    self.parser_dictionary = parser_dictionary(dictionary)
    self.parser_output = parser_output(dictionary)

  def parse(self, c):
    self.parser_dictionary.parse(c)
    return self.parser_output.parse(c)

  def finish(self):
    return self.parser_output.parse_end()

class Decompressor:
  def __init__(self, dictionary, parser_dictionary):
    self.reference = {}
    self.parser_dictionary = parser_dictionary(dictionary)

  def parse(self, c):
    raise NotImplementedError
