from math import ceil
import random

from common.prefix import get_overlap
from shortest_common_superstring.optimal_assignment \
  import optimal_assignment
from shortest_common_superstring.shortest_common_superstring \
  import _remove_subwords,greedy,naive

def dist(w1, w2):
  return len(w1)-1-get_overlap(w1, w2) if w1 != w2 else int(1e4)

def cycle_cover(words):
  dist_matrix = [[dist(w1,w2) for w2 in words] for w1 in words]
  C = optimal_assignment(dist_matrix)
  cycles = []
  visited = [False for _ in words]
  for i,_ in enumerate(words):
    if not visited[i]:
      curr = i
      visited[i] = True
      newcycle = [words[i]]
      while C[curr] != i:
        curr = C[curr]
        visited[curr] = True
        newcycle.append(words[curr])
      cycles.append(newcycle)
  return cycles

def cycle_weight(cycle):
  return sum(dist(w1,w2) for w1,w2 in zip(cycle,cycle[1:]+cycle[:1]))

def cycle_period(cycle):
  return naive(cycle)

def fits(w, cycle):
  '''Checks if w fits cycle and returns a word after which w can be inserted'''
  period = cycle_period(cycle)[1:]
  idx = (period*(ceil(len(w)-1/len(period))+1)).find(w[1:])
  if idx == -1:
    return None
  period_length = 0
  for w1,w2 in zip(cycle, cycle[1:]):
    period_length += dist(w1,w2)
    if period_length > idx:
      return w1
  return cycle[-1]

def canonical_cycle_cover(words):
  C = cycle_cover(words)
  for w in words:
    current_cycle = next((c for c in C if w in c), None)
    best_cycle = max([c for c in C if fits(w,c) is not None], key=cycle_weight)
    if current_cycle != best_cycle:
      fit = fits(w,best_cycle)
      current_cycle.remove(w)
      for w2 in best_cycle:
        if w2 == fit:
          best_cycle.insert(best_cycle.index(w2)+1,w)
  return C

def greedy_insert(cc):
  F,G = ([],[])
  for c in cc:
    if len(c) == 2:
      shorter = len(c[0]) > len(c[1])
      F.append(c[shorter])
      G.append(c[1-shorter])

  eta = greedy(G) if G else '#'
  G.sort(key=lambda g: eta.index(g[1:]))
  Qo,Qe = ([],[])
  for i,pair in enumerate(zip(F,G)):
    f,g = pair
    if i%2 == 1:
      Qo += [f,g]
      Qe += [g,f]
    else:
      Qo += [g,f]
      Qe += [f,g]
  return min([Qo,Qe], key=lambda Qi: len(naive(Qi)))


def shortest_common_superstring(words):
  words = list(_remove_subwords(words))
  C = canonical_cycle_cover(words)
  R = [random.choice(c) for c in C]
  CC = cycle_cover(R)
  Q = greedy_insert(CC)

  alpha = []
  for c in CC:
    if len(c) == 1:
      alpha += c
    if len(c) > 2:
      smallest_overlap = min(zip(c,c[1:]+c[:1]),
          key=lambda pair: get_overlap(pair[0],pair[1]))
      start = smallest_overlap[1]
      alpha += c[c.index(start):] + c[:c.index(start)]
  alpha += Q

  alpha2 = []
  for w in alpha:
    for c in C:
      if w in c:
        alpha2 += c[c.index(w):] + c[:c.index(w)]

  return naive(alpha2)
