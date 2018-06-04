''' Given two generators and functions that map the generated items to integers,
    and a function to merge two such items, produce a single generator.
'''

class _Join_Iterator:
    def __init__(self, merge_fn, gen1, ID_fn1, gen2, ID_fn2):
        self.gen1, self.gen2, self.ID_fn1, self.ID_fn2, self.merge_fn = gen1, gen2, ID_fn1, ID_fn2, merge_fn
    
    def __next__(self):
        self.buf1, self.buf2 = next(self.gen1), next(self.gen2)
        while self.ID_fn1(self.buf1) != self.ID_fn2(self.buf2):
            if self.ID_fn1(self.buf1) < self.ID_fn2(self.buf2):
                self.buf1 = next(self.gen1)
            else: # self.ID_fn1(self.buf1) > self.ID_fn2(self.buf2)
                self.buf2 = next(self.gen2)
        return self.merge_fn(self.buf1, self.buf2)
    
    def __iter__(self): return self

def gen(merge, gen1, ID1, gen2, ID2):
    return _Join_Iterator(merge, gen1, ID1, gen2,ID2)

'''
L1 = [1,2,3,8, 9, 10]
L2 = [2,4,6, 8, 10]

def identity1(x):
    return x

def identity2(x):
    return x

def merge(x,y):
    return x,y

for x in gen(merge, iter(L1), identity1, iter(L2), identity2):
    print(x)

for x in join.gen(lambda x,y: (x,y), iter([1,3, 4, 5, 7,8,9]),  lambda x:x, iter([2,4,6,8,10]), lambda x:x, ):
    print(x)

'''
