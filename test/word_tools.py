class ComparisonCount:
  def __init__(self, w, debug = False):
    self.word, self.compared, self.debug = w, 0, debug

  def __getitem__(self, key):
    self.compared += 1
    if self.debug:
      print(key, self.word[key])
    return self.word[key]

  def __len__(self):
    return len(self.word)
