import numpy as np

def compute_inversed_suffix_array(SA):
    inv_SA = [0] * len(SA)
    for i in range(1, len(SA)):
        inv_SA[SA[i]] = i
    return inv_SA

def compute_seqence_diff(inv_SA, LCP):
    I = [0] * len(inv_SA)
    for i in range(len(inv_SA)):
        I[i] = LCP[inv_SA[i]] + i
    return I

def compute_bit_string(I):
    S = ""
    for i in range(len(I)):
        if i > 0:
            zeros = I[i] - I[i-1]
            if i == 1:
                zeros = I[i]
            S += '0' * zeros
            S += '1'
    return S

def compress_LCP_to_bit_string(LCP, SA):
    INV = compute_inversed_suffix_array(SA)
    I = compute_seqence_diff(INV, LCP)
    return compute_bit_string(I)

class compressed_LCP_2n:
    def __init__(self, S, SA):
        self.SA = SA
        self.S = S
        
    def select_one(self, i):
        # Since structure for this select was not described in paper
        # For simplicity we use naive one
        if i == 0:
            return 0
        for idx in range(len(self.S)):
            if self.S[idx] == '1':
                i -= 1
                if i == 0:
                    return idx+1 # +1 since we index from 0
        raise Exception("Not enough 1s in bit-string")
    
    def lcp(self, i):
        return self.select_one(self.SA[i]) - 2 * self.SA[i]

class compressed_LCP_o_n:
    def __init__(self, S, T, SA, delta):
        
        self.T = T
        self.SA = SA
        
        self.kappa = int(np.log2(len(T))**2)
        self.lambd = int(np.log2(self.kappa )**2)
        
        self.delta = delta # degree of compression
        self.limit = int(np.log2(len(T))**self.delta)
        
        self.last = -1 # index of last interval
        
        self.N = [0 for _ in range(int((len(T) - 1) / self.kappa) + 2)]
        self.H = [0 for _ in range(int((len(T) - 1) / self.kappa) + 2)]
        
        self.compress_bit_string(S)
        
    def compress_bit_string(self, S):
        for i in range(1, len(self.N)):
            if self.kappa * i > len(self.T):
                self.last = i
                self.N[i] = self.brutal_select_one(S, len(self.T)) # last interval
                self.H[i] = self.hardcode_interval(S, self.kappa * (i - 1) + 1, len(self.T)) # inclusive
            else:
                self.N[i] = self.brutal_select_one(S, self.kappa * i)
                interval_size = self.N[i] - self.N[i - 1]
                if interval_size > self.kappa**2:
                    self.H[i] = self.hardcode_interval(S, self.kappa * (i - 1) + 1, self.kappa) # inclusive
                else:
                    self.H[i] = self.compress_interval(S[self.N[i - 1] : self.N[i]])
    
    def compress_interval(self, I):
        N_prime_size = int((self.kappa - 1) / self.lambd) + 2
        N_prime = [0 for _ in range(N_prime_size)]
        H_prime = [0 for _ in range(N_prime_size)]
        for i in range(1, len(N_prime)):
            if self.lambd * i > self.kappa:
                N_prime[i] = self.brutal_select_one(I, self.kappa) # last interval
                H_prime[i] = self.hardcode_interval(I, self.lambd * (i - 1) + 1, self.kappa) # inclusive
            else:
                N_prime[i] = self.brutal_select_one(I, self.lambd * i) # last interval
                mini_interval_size = N_prime[i] - N_prime[i - 1]
                if mini_interval_size > self.limit:
                    H_prime[i] = self.hardcode_interval(I, self.lambd * (i - 1) + 1, self.lambd * i) # inclusive
                else:
                    pass # this case needs iteration through text
        return (N_prime, H_prime)
    
    def brutal_select_one(self, S, i):
        # Since structure for this select for bit string was not described in paper
        # For simplicity we use naive one
        # Used only while compressing
        if i == 0:
            return 0
        for idx in range(len(S)):
            if S[idx] == '1':
                i -= 1
                if i == 0:
                    return idx+1 # +1 since we index from 0
        raise Exception("Not enough 1s in bit-string")
    
    def hardcode_interval(self, S, begin, end): # begin and end are inclusive
        hardcoded = []
        for i in range(begin, end + 1):
            hardcoded.append(self.brutal_select_one(S, i))
        return hardcoded
    
    def select_one(self, i):
        interval_number = int((i - 1) / self.kappa) + 1
        if interval_number == self.last:
            return self.H[interval_number][(i - 1) - (interval_number - 1) * self.kappa ]
        interval_size = self.N[interval_number] - self.N[interval_number - 1]
        if interval_size > self.kappa**2:
            return self.H[interval_number][i - (interval_number - 1) * self.kappa ] # hardcoded
        else:
            mini_interval_number = int(((i-1) % self.kappa) / self.lambd) + 1
            mini_interval_size = self.H[interval_number][0][mini_interval_number] - self.H[interval_number][0][mini_interval_number - 1]
            if mini_interval_size > self.limit:
                a = self.N[interval_number - 1]
                b = self.H[interval_number][1][mini_interval_number][((i - 1) % self.kappa) % self.lambd]
                return a + b # hardcoded
            else:
                a = self.N[interval_number - 1]
                b = self.H[interval_number][0][mini_interval_number - 1]
                return a + b # linear check will be performed
        return 0
    
    def lcp(self, i):
        if i < 2:
            return 0
        approx = self.select_one(self.SA[i]) - 2 * self.SA[i]
        if approx < 0:
            approx = 0
        idx_i = self.SA[i] + approx
        idx_j = self.SA[i - 1] + approx
        T = self.T + '$'
        while T[idx_i] == T[idx_j]:
            approx += 1
            idx_i += 1
            idx_j += 1
        return approx