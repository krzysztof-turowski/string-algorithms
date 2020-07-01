from math import ceil, log

def make_len_2_pow(s):
  x = ceil(log(len(s), 2))
  i = int(pow(2, x))
  return s+"$"*(i-len(s))

def compute_pattern(w:str, t:str, k:int, cur_pat_len:int,
                    b_frst_mm_p:int, end_loop:int, PAT_M, TEXT_M,
                    pattern_m=True): 

  def extend_pattern(cur_p:int, frst_p:int, found_mm:int):
    frst_p = max(frst_p, cur_p)
    frst_p += 1
    while(found_mm < k+1 and (frst_p-cur_p < cur_pat_len+1) and
          not(pattern_m and frst_p>=len(w))):
      if t[frst_p] != w[frst_p-cur_p]:
        found_mm += 1
        TEXT_M[cur_p][found_mm] = frst_p-cur_p
      frst_p += 1
    return frst_p-1

  def merge_pattern(cur_p:int, b_frst_mm_p:int, frst_p:int):
    t_it, p_it, no_mm = 0, 1, 0
    for x in range(1, k+3):
      if b_frst_mm_p + TEXT_M[b_frst_mm_p][x] > cur_p :
        t_it = x
        break

    w_slide = cur_p-b_frst_mm_p
    while not(no_mm == k+1 or t_it == k+2 or
              (cur_p + PAT_M[w_slide][p_it]>frst_p
               and TEXT_M[b_frst_mm_p][t_it] == len(w))):
      if cur_p+PAT_M[w_slide][p_it] > b_frst_mm_p + TEXT_M[b_frst_mm_p][t_it]:
        no_mm += 1
        TEXT_M[cur_p][no_mm] = TEXT_M[b_frst_mm_p][t_it] - (w_slide)
        t_it += 1
      elif cur_p+PAT_M[w_slide][p_it] < b_frst_mm_p + TEXT_M[b_frst_mm_p][t_it]:
        no_mm += 1
        TEXT_M[cur_p][no_mm] = PAT_M[cur_p-b_frst_mm_p][p_it]
        p_it += 1
      else:
        if w[PAT_M[w_slide][p_it]] != t[cur_p+PAT_M[w_slide][p_it]]:
          no_mm +=1
          TEXT_M[cur_p][no_mm] = PAT_M[w_slide][p_it]
        p_it +=1
        t_it +=1
    return no_mm

  frst_p = b_frst_mm_p
  for cur_p in range(b_frst_mm_p, end_loop):
    found_mm = 0
    if pattern_m:
      frst_p = min(frst_p, len(w)-1)
    if cur_p < frst_p:
      found_mm = merge_pattern(cur_p, b_frst_mm_p, frst_p)
    if found_mm < k + 1:
      b_frst_mm_p = cur_p
      if pattern_m:
        b_frst_mm_p = 1
      frst_p = extend_pattern(cur_p, frst_p, found_mm)

def pattern_matching(w: str, k: int, m: int):
  PAT_M = [[]]
  m_log = int(log(m, 2))
  for x, y in ((2**p, m//(2**(p+1))) for p in range(m_log)):
    for _ in range(x, 2*x):
      PAT_M.append([m+1]*(min(y*2*k+1, m-x)+2))
    compute_pattern(w, w, min(y*2*k+1, m-x), m-x, x, 2*x, PAT_M, PAT_M)
  return PAT_M

def text_matching(w: str, t:str, k:int, PAT_M):
  TEXT_M = [[len(w)]*(k+3)]
  res = []
  for i in range(1, len(t)-len(w)+1):
    TEXT_M.append([len(w)]*(k+3))
  compute_pattern(w, t, k, len(w)-1, 0, len(t)-len(w)+1,
                  PAT_M, TEXT_M, False)
  for i in range(len(t)-len(w)+1):
    if TEXT_M[i][k+1] == len(w):
      res.append(i)
  return res

def string_matching_with_mismatches(t: str, w: str, n:int, m:int, k:int):
  if k > len(w):
    res = list(range(n-m+1))
  else:
    pat_p = make_len_2_pow(w)
    p = pattern_matching('$'+pat_p, k, len(pat_p))
    for i, p_list in enumerate(p):
      for j, x in enumerate(p_list):
        if x + i > len(w):
          p[i][j] = len(w) + 1
    res = text_matching('$'+w, '$'+t, k, p)
  for ret in res:
    yield ret

def compare_strings(s, t, k:int):
  x = 0
  for i, _ in enumerate(s):
    if s[i] != t[i]:
      x += 1
  if x > k:
    return False
  return True

def brute_search(t:str, w:str, n:int, m:int, k:int):
  res = []
  for i in range(n - m+1):
    x = compare_strings(w, t[i:i+m], k)
    if x:
      res.append(i)
  return res
