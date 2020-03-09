class ComparisonCount:
  def __init__(self, w):
    self.w, self.compared = w, 0

  def __getitem__(self, key):
    self.compared += 1
    return self.w[key]

  def __len__(self):
    return len(self.w)
