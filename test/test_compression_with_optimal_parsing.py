from compression import lzw

test_0 = "abababaabaabaaab"
test_1 = "abccdeabccdeacdeacdeacde"

def lzw_compress():
  w = test_1

  alphabet = set()
  for c in w:
    alphabet.add(c)
  alphabet = sorted(alphabet)

  instance = lzw.LZW(alphabet)
  for c in w:
    instance.parse(c)
  return instance.finish()
