def fibonacci_word(m):
  '''Generates m-th Fibonacci word'''
  f, f_previous = '0', '1'
  for i in range(m):
    f, f_previous = f + f_previous, f
  return '#' + f

def fibonacci_word_morphism(m):
  '''Generates m-th Fibonacci word via morphism'''
  f = '0'
  for i in range(m):
    f = f.replace('0', '0_').replace('1', '0').replace('_', '1')
  return '#' + f

def thue_word(m):
  '''Generates m-th Thue-Morse word'''
  return thue_word_morphism(m)

def thue_word_morphism(m):
  '''Generates m-th Thue-Morse word via morphism'''
  t = '0'
  for i in range(m):
    t = t.replace('0', '0_').replace('1', '10').replace('_', '1')
  return '#' + t
