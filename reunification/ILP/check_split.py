#!/usr/bin/env python3

import sys
from os.path import splitext
from collections import defaultdict

input_filename, asst_filename = sys.argv[1:]


class Node:

    def __init__(self):
        self.wt = 0
        self.nbrs = []

    def add_nbr(self, *others):
        self.nbrs.extend(others)


centers = defaultdict(lambda: Node())
splits = defaultdict(lambda: Node())

with open(input_filename) as f:
    for line in f:
        if line.strip():
            line = [int(x) for x in line.split()]
            assert len(line) % 2 == 1
            s, *line = line
            for c, n in (line[2*i:2*i+2] for i in range(int(len(line)/2))):
                splits[s].wt += n
                centers[c].wt += n
                splits[s].add_nbr(c)
                centers[c].add_nbr(s)

split_wt = sum(s.wt for s in splits.values())
center_wt = sum(c.wt for c in centers.values())
assert split_wt == center_wt
print(len(splits), "blocks.", len(centers), "districts. total population", split_wt)

# edges = [(s, c) for s in splits for c in splits[s].nbrs]

splits_of_center = defaultdict(lambda: set())
centers_of_split = defaultdict(lambda: set())

with open(asst_filename) as f:
    for line in f:
        if line.strip():
            s, c = [int(x) for x in line.split()]
            centers_of_split[s].add(c)
            splits_of_center[c].add(s)

for s in splits:
    if len(centers_of_split[s]) != 1:
        print("error: split", s, "assigned to centers", list(centers_of_split[s]))

discrepancy = max(
    abs(sum(splits[s].wt for s in splits_of_center[c]) - centers[c].wt)
    for c in centers
)

print("max discrepancy is", discrepancy)
