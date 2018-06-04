''' Given two generators and functions that map the generated items to integers,
    and a function to merge two such items, produce a single generator.
'''

class _Join_Iterator:
    def __init__(self, gen1, gen2, ID_fn1, ID_fn2, merge_fn):
        self.gen1, self.gen2, self.ID_fn1, self.ID_fn2, self.merge_fn = gen1, gen2, ID_fn1, ID_fn2, merge_fn
    
    def __next__(self):
        self.buf1, self.buf2 = next(self.gen1), next(self.gen2)
        print("buf0 ", self.buf1, self.buf2)
        while self.ID_fn1(self.buf1) != self.ID_fn2(self.buf2):
            if self.ID_fn1(self.buf1) < self.ID_fn2(self.buf2):
                self.buf1 = next(self.gen1)
                print("buf1 ", self.buf1, self.buf2)
            else: # self.ID_fn1(self.buf1) > self.ID_fn2(self.buf2)
                self.buf2 = next(self.gen2)
                print("buf2 ", self.buf1, self.buf2)
        return self.merge_fn(self.buf1, self.buf2)
    
    def __iter__(self): return self

def gen(gen1, gen2, ID1, ID2, merge):
    return _Join_Iterator(gen1, gen2, ID1, ID2, merge)

'''
L1 = [1,2,3,8, 9, 10]
L2 = [2,4,6, 8, 10]

def identity1(x):
    return x

def identity2(x):
    return x

def merge(x,y):
    return x,y

for x in gen(iter(L1), iter(L2), identity1, identity2, merge):
    print(x)

for x in join.gen(iter([1,3, 4, 5, 7,8,9]),iter([2,4,6,8,10]),lambda x:x, lambda x:x, lambda x,y: (x,y)):
    print(x)

'''
