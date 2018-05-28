#!/usr/bin/env python3

import sys
from os.path import splitext
from collections import defaultdict
import gurobipy as gp

input_filename = 'California_boundary_districts.txt'
input_filename = 'tabblock2010_44_pophu-2-split.output'

basename = splitext(input_filename)[0]
output_filename = basename + '_gurobi_asst.txt'
log_filename = basename + '_gurobi_log.txt'

input = open(input_filename).read()
output = open(output_filename, "w")
sys.stdout = open(log_filename, "w")


class Node:

    def __init__(self):
        self.wt = 0
        self.nbrs = []

    def add_nbr(self, *others):
        self.nbrs.extend(others)


centers = defaultdict(lambda: Node())
splits = defaultdict(lambda: Node())

for line in input.split("\n"):
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

edges = [(s, c) for s in splits for c in splits[s].nbrs]

m = gp.Model("m")
value = m.addVar()
assignments = m.addVars(edges, vtype=gp.GRB.BINARY)
discrepancies = m.addVars(centers, lb=-gp.GRB.INFINITY)

# assign each split to one center
for s in splits:
    m.addConstr(1 == gp.quicksum(assignments[s, c] for c in splits[s].nbrs))

# discrepancy of each center
for c in centers:

    m.addConstr(
        discrepancies[c]
        == centers[c].wt
        - gp.quicksum(splits[s].wt * assignments[s, c] for s in centers[c].nbrs)
    )

    # max discrepancy
    m.addConstr(value >= discrepancies[c])
    m.addConstr(value >= -discrepancies[c])

m.setObjective(value, gp.GRB.MINIMIZE)

m.optimize()

# for c in sorted(centers):
#     print(
#         f"center {c} assigned splits",
#         [f"{s}@{splits[s].wt}" for s in centers[c].nbrs if assignments[s, c].x == 1],
#         f". target {centers[c].wt}. discrepancy {discrepancies[c].x}.",
#     )

print("max discrepancy is", m.objVal)

for s in sorted(splits):
    c = [c for c in splits[s].nbrs if assignments[s, c].x == 1]
    assert len(c) == 1
    print(s, c[0], file=output)

# for some reason this is necessary so output is not truncated
output.close()
