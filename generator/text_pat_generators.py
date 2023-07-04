import random
import string
import scipy.stats

class uniform_generator:
    def generate(n, m, *, A = string.ascii_lowercase):
        t = ''.join(random.choice(A) for i in range(n))
        w = ''.join(random.choice(A) for i in range(m))
        return (t, w)

class geometric_generator:
    def generate(n, m, *, A = string.ascii_lowercase, p = 0.5):
        choice = [v for i, v in enumerate(A) for _ in range(int(1000*scipy.stats.geom.pmf(i+1, p)))]
        print(choice)
        t = ''.join(random.choice(choice) for i in range(n))
        w = ''.join(random.choice(choice) for i in range(m))
        return (t, w)

class natural_generator:
    def __init__(self, filename):
        with open(filename, 'r') as file:
            data = file.read().replace('\n', ' ')
            data = ' '.join(data.split())
            data = data.lower()
            data = ''.join(e for e in data if e.isalnum() or e == ' ')
            self.data = data
    
    def generate(self, n, m):
        t_ind = random.randint(0, len(self.data)-n-1)
        t = self.data[t_ind:t_ind+n+1]
        w_ind = random.randint(0, len(t)-m-1)
        w = t[w_ind:w_ind+m]
        return (t, w)

class bf_hard_generator:
    def generate(n):
        t = 'a' * n + 'b'
        w = 'a' * (n//2) + 'b'
        return (t, w)

class bm_hard_generator:
    def generate(n, m):
        t = 'a' * n
        w = 'a' * m
        return (t, w)

class ag_hard_generator:
    def generate(n, m):
        x = (m-2)//2
        e = n//m
        w = 'a' * (x-1) + 'b' + 'a' * x + 'b'
        t = w * e
        return (t, w)
