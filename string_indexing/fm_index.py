
class FMIndex:
   
   # all of strings beginns with # (idk why?)
   # i sppose that patterns do not starts with #
   
   def __init__ (self, SA, BWT, text, n):
      self.L = BWT
      self.F = '#$' + ''.join(text[SA[i]] for i in range(1, n + 1))
      self.n = n
      self.SA = SA
      self.sampleSize = 8 # const for sampling

      #prepare char mapping for F
      self.mapperOfChar = { self.F[2] : 0}
      self.begginings = [2]
      last = self.F[2]
      lenOfBeginings = 1
      for i in range(3, n+2):
         if self.F[i] != last:
            last = self.F[i]
            self.begginings.append(i)
            self.mapperOfChar[last] = lenOfBeginings
            lenOfBeginings += 1

      self.lenOfAlphabet = len(self.mapperOfChar)
      
      #prepare closest samplings
      currentSample = 0
      self.closestSample = [0]
      for i in range(1, n+2):
         if abs(currentSample-i) > abs(currentSample + self.sampleSize-i) and (i + self.sampleSize < self.n):
            currentSample += self.sampleSize
         self.closestSample.append(currentSample)

      #Generate values for occ for given samples O(|A|*n)
      self.occInSampleForChar = { self.L[i]: [0] for i in range(1, n+2)}
      for c in self.mapperOfChar:
         currValue = 0
         nextSample = self.sampleSize
         for i in range(1, n+2):
            if self.L[i] == c:
               currValue += 1
            if i == nextSample:
               self.occInSampleForChar[c].append(currValue)
               nextSample = nextSample + self.sampleSize

    # should be private
   def getRangeOfOccurence(self, p, size):
      if size > self.n:
        return [-1, -1]
      
      currChar = p[size-1]
      if currChar not in self.mapperOfChar:
         return [-1, -1]

      mapIdx = self.mapperOfChar[currChar]
      l = self.begginings[mapIdx]
      r = self.n + 1
      if mapIdx != self.lenOfAlphabet - 1:
         r = self.begginings[mapIdx + 1] - 1
      
      for i in range(size-2, -1, -1):
         currChar = p[i]
         if currChar not in self.mapperOfChar:
            return [-1, -1]
         occurencesBefore = self._getOcc(currChar, l - 1)
         occurencesAfter = self._getOcc(currChar, r)
         if occurencesBefore == occurencesAfter:
            return [-1, -1]
         mapIdx = self.mapperOfChar[currChar]
         l = self.begginings[mapIdx] + occurencesBefore
         r = self.begginings[mapIdx] + occurencesAfter - 1
         if r < l:
            return [-1, -1]
      return [l, r]

    # O(|p|)
   def count(self, p, size):
      ran = self.getRangeOfOccurence(p, size)
      if ran[0] == -1:
         return 0
      return max(ran[1] - ran[0] + 1, 0)


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
         
      return self.occInSampleForChar[c][(closestSample)//self.sampleSize] + toAdd
      
    #O(|p|)
   def query(self, p, l):
      return self.count(p, l) > 0
   
   # O(|p| + k) where k is the number or occurances of p in text
   def get_all_occurrance(self, p, l):
      arr = self.getRangeOfOccurence(p, l)
      if arr[0] == -1:
         return []
      return [self.SA[i-1] for i in range(arr[0], arr[1] + 1)]

    # O(|p|)
   def get_any_occurrance(self, p, l):
      arr = self.getRangeOfOccurence(p, l)
      if arr[0] == -1:
         return -1
      return self.SA[arr[0]-1]
   
