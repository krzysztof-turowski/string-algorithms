from common import prefix

def brute_force(t, w, n, m):
  i = 1
  while i <= n - m + 1:
    j = 0
    while j < m and t[i + j] == w[j + 1]:
      j = j + 1
    if j == m:
      yield i
    i = i + 1

def morris_pratt(t, w, n, m):
  B = prefix.prefix_suffix(w, m)
  i, j = 1, 0
  while i <= n - m + 1:
    while j < m and t[i + j] == w[j + 1]:
      j = j + 1
    if j == m:
      yield i
    i, j = i + j - B[j], max(0, B[j])

def knuth_morris_pratt(t, w, n, m):
  sB = prefix.strong_prefix_suffix(w, m)
  i, j = 1, 0
  while i <= n - m + 1:
    while j < m and t[i + j] == w[j + 1]:
      j = j + 1
    if j == m:
      yield i
    i, j = i + j - sB[j], max(0, sB[j])

def galil_seiferas(text, word, n, m):
  K= 4
  s,p1,q1= 0,1,0
  p2,q2= 0,0
  mode=0
  while True:
    if mode==1:
      #Znajdź najkrótszy k-okres prefiksu word[s+1:]
      while s+p1+q1 < m and word[s+p1+q1+1] == word[s+q1+1]: q1+= 1
      if p1+q1 >= p1*K: p2, q2= q1,0; mode=2; continue
      if s+p1+q1 == m: break
      p1+= (1 if q1==0 else (q1+K-1)//K); q1= 0
    elif mode==2:
      #Znajdź drugi najkrótszy okres prefiksu word[s+1:]. Jeśli nie istnieje to przejdź do drugiej fazy algorytmu.
      while s+p2+q2 < m and word[s+p2+q2+1] == word[s+q2+1] and p2+q2 < p2*K: q2+= 1
      if p2+q2 == p2*K: mode= 0; continue;
      if s+p2+q2 == m: break
      if q2 == p1+q1:
        p2+= p1; q2-= p1;
      else:
        p2+= (1 if q2==0 else (q2+K-1)//K); q2= 0
    else:
      #Zinkrementuj s
      while s+p1+q1 < m and word[s+p1+q1+1] == word[s+q1+1]: q1+= 1
      while p1+q1 >= p1*K: s+= p1; q1-= p1;
      p1+= (1 if q1==0 else (q1+K-1)//K); q1= 0
      if p1 >= p2: mode= 1
  #search
  p2,q2= 0,0
  while True:
    while p2+s+q2 < n and s+q2 < m and text[p2+s+q2+1] == word[s+q2+1]: q2+= 1
    if q2 == m-s and text[p2+1 : p2+s+1] == word[1 : s+1]:
      yield p2+1
    if q2 == p1+q1:
      p2+= p1; q2-= p1
    else:
      p2+= (1 if q2==0 else (q2+K-1)//K); q2= 0
    if p2+s > n: return
