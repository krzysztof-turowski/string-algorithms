from compression.core import parser
from compression.core.dictionary import SimpleDict, TrieDict

class LZW:

  def __init__(self, alphabet):
    self.dictionary = TrieDict('$')
    self.reverse_dictionary = TrieDict('$')
    self.parser_dictionary = parser.LZWTrieDictParser(
        self.dictionary, self.reverse_dictionary, len(alphabet)
    )
    self.parser_output = parser.OptimalOutputParser(
        self.dictionary, self.reverse_dictionary
    )

    self.dictionary.connect(self.reverse_dictionary)
    self.reverse_dictionary.connect(self.dictionary)
    print(alphabet)
    for i in range(len(alphabet)):
      node = self.dictionary.insert(alphabet[i], i)
      rev_node = self.reverse_dictionary.insert(alphabet[i], i)
      print(type(node), type(rev_node))
      node.connect(rev_node)
      rev_node.connect(node)
    print(self.dictionary.children)
    print(self.reverse_dictionary.children)
    self.it = 1

  def parse(self, c):
    print("{2} ({0}): {1}".format(c, self.parser_output.parse(c), self.it))
    print("{2} ({0}): {1}".format(c, self.parser_dictionary.parse(c), self.it))
    self.it += 1

  def finish(self):
    self.parser_output.parse_end()
    return self.parser_output.output

class LZWDec:

  def __init__(self, alphabet):
    self.reference = {}
    self.dictionary = TrieDict('$')
    self.reverse_dictionary = TrieDict('$')
    self.parser_dictionary = parser.LZWTrieDictParser(
        self.dictionary, self.reverse_dictionary, len(alphabet)
    )

    print(alphabet)
    for i in range(len(alphabet)):
      node = self.dictionary.insert(alphabet[i], i)
      self.reference[i] = node
    self.it = 1

  def parse(self, c):
    c = int(c)
    if c in self.reference:
      print('mam kod', c)
      node = self.reference[c]
      tmp = ""
      while node.parent != node:
        tmp += node.edge
        node = node.parent
      tmp = tmp[::-1]
      for x in tmp:
        print('parse', x)
        added = self.parser_dictionary.parse(x)
        if added is not None:
          self.reference[added.label] = added
      return tmp
    # else self.reference[c] is None
    print('nie mam jeszcze kodu', c)
    node = self.parser_dictionary.temp_phrase
    tmp = ""
    while node.parent != node:
      tmp += node.edge
      node = node.parent
    tmp = tmp[::-1]
    tmp2 = tmp
    ans = ""
    for x in tmp:
      print('parse', x)
      tmp2 += x
      added = self.parser_dictionary.parse(x)
      if added is not None:
        self.reference[added.label] = added
        if added.label == c:
          ans = tmp2
        # break
        # break or not to break?
    for x in ans[len(tmp):]:
      print('parse', x)
      added = self.parser_dictionary.parse(x)
      if added is not None:
        self.reference[added.label] = added
    print('a teraz juz mam?', c in self.reference)
    return ans

class LZ78:

  def __init__(self, alphabet):
    self.dictionary = TrieDict('$', index=0)
    self.reverse_dictionary = TrieDict('$', index=0)
    self.parser_dictionary = parser.LZ78TrieDictParser(
        self.dictionary, self.reverse_dictionary, 0
    )
    self.parser_output = parser.OptimalOutputParser(
        self.dictionary, self.reverse_dictionary
    )

    self.dictionary.connect(self.reverse_dictionary)
    self.reverse_dictionary.connect(self.dictionary)
    print(alphabet)
    for i in range(len(alphabet)):
      break
      node = self.dictionary.insert(alphabet[i], (0, alphabet[i], i+1), i+1)
      rev_node = self.reverse_dictionary.insert(alphabet[i], (0, alphabet[i], i+1), i+1)
      print(type(node), type(rev_node))
      node.connect(rev_node)
      rev_node.connect(node)
    print(self.dictionary.children)
    print(self.reverse_dictionary.children)
    self.it = 1

  def parse(self, c):
    print("{2} ({0}): {1}".format(c, self.parser_dictionary.parse(c), self.it))
    print("{2} ({0}): {1}".format(c, self.parser_output.parse(c), self.it))
    self.it += 1

  def finish(self):
    self.parser_output.parse_end()
    return self.parser_output.output

class LZ78Dec:

  def __init__(self, alphabet):
    self.reference = {}
    self.dictionary = TrieDict('$')
    self.reverse_dictionary = TrieDict('$')
    self.parser_dictionary = parser.LZ78TrieDictParser(
        self.dictionary, self.reverse_dictionary, 0
    )
    self.reference[0] = self.dictionary
    return
    print(alphabet)
    for i in range(len(alphabet)):
      node = self.dictionary.insert(alphabet[i], (0, alphabet[i]))
      self.reference[i] = node
    self.it = 1

  def parse(self, d):
    c = d[0]
    if c in self.reference:
      print('mam kod', c)
      node = self.reference[c]
      tmp = d[1]
      while node.parent != node:
        tmp += node.edge
        node = node.parent
      tmp = tmp[::-1]
      for x in tmp:
        print('parse', x)
        added = self.parser_dictionary.parse(x)
        if added is not None:
          print('added', added.index)
          self.reference[added.index] = added
      return tmp
    # else self.reference[c] is None
    print('nie mam jeszcze kodu', c)
    node = self.parser_dictionary.temp_phrase
    tmp = ""
    while node.parent != node:
      tmp += node.edge
      node = node.parent
    tmp = tmp[::-1]
    tmp2 = tmp
    ans = ""
    for x in tmp:
      print('parse', x)
      tmp2 += x
      added = self.parser_dictionary.parse(x)
      if added is not None:
        self.reference[added.label] = added
        if added.label == c:
          ans = tmp2
        # break
        # break or not to break?
    for x in ans[len(tmp):]:
      print('parse', x)
      added = self.parser_dictionary.parse(x)
      if added is not None:
        self.reference[added.label] = added
    print('a teraz juz mam?', c in self.reference)
    return ans
