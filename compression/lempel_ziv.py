def lz77(text, n):
  data, index = [], 1
  while index <= n:
      offset, length = 0, 0
      for i in range(1, index):
          l = 0
          while index + l < n and text[index - i + l] == text[index + l]:
              l += 1
          if l > length:
              offset, length = i, l
      data.append((offset, length, text[index + length]))
      index += length + 1
  return data

def inverse_lz77(data):
  text = '#'
  for offset, length, c in data:
    if offset == 0 and length == 0:
      text += c
    else:
      while offset <= length:
        text, length = text + text[-offset:], length - offset
      text += text[-offset:-offset + length] + c
  return text
