class Segment:
    eps = 0
    def __init__(self, pt_pair):
        ((self.x1, self.y1), (self.x2, self.y2)) = pt_pair
    
    def pt1(self): return (self.x1, self.y1)
    
    def pt2(self): return (self.x2, self.y2)

    def swap(self): return Segment( ((self.x2, self.y2), (self.x1, self.y1)) )
    
    def pt_pair(self): return ((self.x1, self.y1), (self.x2, self.y2))

    def __eq__(self, other):
        if self.eps == 0:
            return self.x1==other.x1 and self.y1==other.y1 and self.x2==other.x2 and self.y2==other.y2
        else:
            return int(self.x1/self.eps)==int(other.x1/self.eps) and int(self.y1/self.eps)==int(other.y1/self.eps) and int(self.x2/self.eps)==int(other.x2/self.eps) and int(self.y2/self.eps)==int(other.y2/self.eps)
    
    def __hash__(self):
        if self.eps == 0: return hash((self.x1, self.y1, self.x2, self.y2))
        return hash((int(self.x1/self.eps),int(self.y1/self.eps),int(self.x2/self.eps),int(self.y2/self.eps)))
    
