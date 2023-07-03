import random
import string
from scipy.stats import geom

class uniform_generator:
    def generate(text_len, pat_len, alph = string.ascii_lowercase):
        text = ''.join(random.choice(alph) for i in range(text_len))
        pat = ''.join(random.choice(alph) for i in range(pat_len))
        return (text, pat)

class geometric_generator:
    def generate(text_len, pat_len, alph = string.ascii_lowercase, p = 0.5):
        choice = []
        for i, val in enumerate(alph):
            choice += [val for j in range(int(1000*geom.pmf(i+1,p)))]
        text = ''.join(random.choice(choice) for i in range(text_len))
        pat = ''.join(random.choice(choice) for i in range(pat_len))
        return (text, pat)

class natural_generator:
    data = ""
    with open('pantadeusz.txt', 'r') as file:
        data = file.read().replace('\n', ' ')
        data = ' '.join(data.split())
        data = data.lower()
        data = ''.join(e for e in data if e.isalnum() or e == ' ')
        data = data[1000:11000]
    
    @classmethod
    def generate(cls, text_len, pat_len):
        text_ind = random.randint(0, len(cls.data)-text_len-1)
        text = cls.data[text_ind:text_ind+text_len+1]
        pat_ind = random.randint(0, len(text)-pat_len-1)
        pat = text[pat_ind:pat_ind+pat_len]
        return (text, pat)

class bf_hard_generator:
    def generate(text_len):
        text = 'a' * text_len + 'b'
        pat = 'a' * (text_len // 2) + 'b'
        return (text, pat)

class bm_hard_generator:
    def generate(text_len, pat_len):
        text = 'a' * text_len
        pat = 'a' * pat_len
        return (text, pat)

class ag_hard_generator:
    def generate(text_len, pat_len):
        m = (pat_len - 2) // 2
        e = text_len // pat_len
        pat = 'a' * (m - 1) + 'b' + 'a' * (m) + 'b'
        text = pat * e
        return (text, pat)
