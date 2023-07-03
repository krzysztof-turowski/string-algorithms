class benchar:
    def __init__(self):
        self.cmp_count = 0
    
    def __call__(self, *args, **kwargs):
        base_str = str(*args, **kwargs)
        return benchar.count_str(base_str, self)

    def _first_diff(a, b):
        for i in range(min(len(a), len(b))):
            if str.__ne__(a[i], b[i]):
                return i + 1
        return min(len(a), len(b))
    
    class count_str(str):
        def __new__(cls, base_str, parent_benchar):
            obj = str.__new__(cls, base_str)
            obj._parent_benchar = parent_benchar
            return obj

        def __getitem__(self, key):
            obj = str.__getitem__(self, key)
            obj = benchar.count_str(obj, self._parent_benchar)
            return obj
        
        def __add__(self, other):
            obj = str.__add__(self, other)
            obj = benchar.count_str(obj, self._parent_benchar)
            return obj
        
        def __iter__(self):
            obj = str.__iter__(self)
            obj = benchar.count_str_iterator(obj, self._parent_benchar)
            return obj
        
        def __eq__(self, other):
            res = str.__eq__(self, other)
            self._parent_benchar.cmp_count += benchar._first_diff(self, other)
            return res

        def __ne__(self, other):
            res = str.__ne__(self, other)
            self._parent_benchar.cmp_count += benchar._first_diff(self, other)
            return res

        def __lt__(self, other):
            res = str.__lt__(self, other)
            self._parent_benchar.cmp_count += benchar._first_diff(self, other)
            return res

        def __le__(self, other):
            res = str.__le__(self, other)
            self._parent_benchar.cmp_count += benchar._first_diff(self, other)
            return res

        def __gt__(self, other):
            res = str.__gt__(self, other)
            self._parent_benchar.cmp_count += benchar._first_diff(self, other)
            return res
        
        def __ge__(self, other):
            res = str.__ge__(self, other)
            self._parent_benchar.cmp_count += benchar._first_diff(self, other)
            return res
        
        def endswith(self, other):
            res = str.endswith(self, other)
            if(len(self) >= len(other)):
                self._parent_benchar.cmp_count += benchar._first_diff(self[-len(other):], other)
            return res
        
        def __hash__(self):
            res = str.__hash__(self)
            return res

    class count_str_iterator:
        def __init__(self, base_str_iterator, parent_benchar):
            self.base_str_iterator = base_str_iterator
            self._parent_benchar = parent_benchar
        
        def __iter__(self):
            return self.base_str_iterator.__iter__()
        
        def __next__(self):
            res = self.base_str_iterator.__next__()
            res = benchar.count_str(res, self._parent_benchar)
            return res
