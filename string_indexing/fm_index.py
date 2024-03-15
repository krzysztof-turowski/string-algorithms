from suffix_array import naive
#from compression import burrows_wheeler
#from compression.burrows_wheeler import transform_from_suffix_array
#from compression.burrows_wheeler import inverse_transform_naive
def transform_from_suffix_array(SA, text, n):
  return '#' + ''.join(
      text[SA[i] - 1] if SA[i] > 1 else '$' for i in range(n + 1))

def inverse_transform_naive(BWT, n):
  reversal = [''] * (n + 1)
  for _ in range(n + 1):
    reversal = [c + r for (r, c) in zip(sorted(reversal), BWT[1:])]
  return '#' + ''.join(sorted(reversal)[0][1:])

def get_L_from_SA(SA, text, n):
    return '#$' + ''.join(text[SA[i]] for i in range(1, n + 1))


class FMIndex:
   
   # all of strings beginns with # (idk why?)
   # F is first characters from suffixes in order from suffix array with $ at the beggining
   # L is result of BWT
   def __init__ (self, F, L, n):
      self.L = L
      self.F = F
      self.n = n
      self.sampleSize = 8 # const for sampling

      #prepare char mapping for F
      self.mapperOfChar = { F[2] : 0}
      self.begginings = [2]
      last = F[2]
      lenOfBeginings = 1
      for i in range(3, n+2):
         if F[i] != last:
            last = F[i]
            self.begginings.append(i)
            self.mapperOfChar[last] = lenOfBeginings
            lenOfBeginings += 1

      self.lenOfAlphabet = len(self.mapperOfChar)
      
      #prepare closest samplings
      currentSample = 1
      self.closestSample = [1, 1]
      for i in range(2, n+2):
         if abs(currentSample-i) > abs(currentSample + self.sampleSize-i) and i + self.sampleSize < self.n:
            currentSample += self.sampleSize
         self.closestSample.append(currentSample)

      #Generate values for occ for given samples O(|A|*n)
      self.occInSampleForChar = { i: [0] for i in self.mapperOfChar}
      for c in self.mapperOfChar:
         currValue = 0
         nextSample = 1 + self.sampleSize
         for i in range(2, n+2):
            if L[i] == c:
               currValue += 1
            if i == nextSample:
               self.occInSampleForChar[c].append(currValue)
      
      print(self.begginings)
      print(self.mapperOfChar)

   def count(self, p, size):
      if size > self.n:
        return 0
      
      currChar = p[size-1]
      if currChar not in self.mapperOfChar:
         return 0
      
      mapIdx = self.mapperOfChar[currChar]
      l = self.begginings[mapIdx]
      r = self.n + 1
      if mapIdx != self.lenOfAlphabet - 1:
         r = self.begginings[mapIdx + 1] - 1
      
      for i in range(size-2, -1, -1):
         currChar = p[i]
         if currChar not in self.mapperOfChar:
            return 0
         occurencesBefore = self._getOcc(currChar, l - 1)
         occurencesAfter = self._getOcc(currChar, r)
         if occurencesBefore == occurencesAfter:
            return 0
         mapIdx = self.mapperOfChar[currChar]
         l = self.begginings[mapIdx] + occurencesBefore
         r = l + occurencesAfter - 1
      return r - l + 1


    #Should be private
   def _getOcc(self, c, i):
      closestSample = self.closestSample[i]
      toAdd = 0
      if closestSample < i:
         for j in range(closestSample + 1, i + 1):
            if self.L[j] == c:
               toAdd += 1
      elif closestSample > i:
         for j in range(i+1, closestSample + 1):
            if self.L[j] == c:
               toAdd -= 1
         
      return self.occInSampleForChar[c][(closestSample-1)//self.sampleSize] + toAdd
      

   def query(self, p, l):
      return self.count(p, l) > 0
        


text = '#abaaba'
n = 6
SA = naive(text, n)
bwt = transform_from_suffix_array(SA, text, n)
revBWT = inverse_transform_naive(bwt, n)
print(text)
print(SA)
print(bwt)
F = get_L_from_SA(SA, text, n)
L = bwt
print(F)
index = FMIndex(F, L, n)
print(index.count('aa', 2))
print(index.count('aab', 3))
print(index.count('a', 1))
print(index.count('b', 1))
print(index.count('aba', 3))
print(index.count('c', 1))
print(index.count('caab', 4))
print(index.count('abaaba', 6))
