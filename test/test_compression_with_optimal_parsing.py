from compression import lzw
from ast import literal_eval as make_tuple

test_0 = "abababaabaabaaab"
test_1 = "abccdeabccdeacdeacdeacde"
test_2 = "a"
test_3 = ""
test_4 = "abbbcaabbcbbcaaac"
test_5 = "ababcbababaa"
test_6 = "aaabbabaabaaabab"
test_7 = "abababcccacadcadaabcada"

def get_test_word():
  w = test_7

  alphabet = set()
  for c in w:
    alphabet.add(c)
  alphabet = sorted(alphabet)

  return (w, alphabet)

def lzw_compress():
  (w, alphabet) = get_test_word()
  instance = lzw.LZW(alphabet)
  for c in w:
    instance.parse(c)
  return instance.finish()

def lzw_decompress():
  (w, alphabet) = get_test_word()
  compressed = lzw_compress()
  instance = lzw.LZWDec(alphabet)
  codes = compressed.split(",")[:-1]
  print('codes:', codes)
  dec_w = ""
  for c in codes:
    tmp_pr = instance.parse(c)
    print(tmp_pr)
    dec_w += tmp_pr
  print(w)
  print(codes)
  print(dec_w)
  print(w == dec_w)

def lz78_compress():
  (w, alphabet) = get_test_word()
  instance = lzw.LZ78(alphabet)
  for c in w:
    instance.parse(c)
  return instance.finish()

def lz78_decompress():
  (w, alphabet) = get_test_word()
  compressed = lz78_compress()
  print('compressed', compressed)
  instance = lzw.LZ78Dec(alphabet)
  codes = compressed.split("),")[:-1]
  print('codes:', codes)
  dec_w = ""
  for c in codes:
    c += ')'
    ct = make_tuple(c)
    print('aaa', c, ct, type(ct))
    tmp_pr = instance.parse(ct)
    print(tmp_pr)
    dec_w += tmp_pr
  print(w)
  print(dec_w)
  print(w == dec_w)

