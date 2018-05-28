#!/usr/bin/env python3

import sys
from os.path import splitext
from collections import defaultdict
from optlang.glpk_interface import Model, Variable, Constraint, Objective

# https://github.com/biosustain/optlang
# sudo port install glpk py36-six py36-simpy 
# pip install --upgrade --user optlang   # (should also install swiglpk)

from contextlib import contextmanager
from timeit import default_timer as timer


@contextmanager
def timed(before):
    print(before, end="", flush=True)
    start = timer()
    yield
    stop = timer()
    print(f" ({stop-start:.2g}s)", flush=True)


input_filename = 'boundary_districts.txt'
input_filename = 'tabblock2010_44_pophu-2-split.output'

basename = splitext(input_filename)[0]
output_filename = basename + '_optlang_asst.txt'
log_filename = basename + '_optlang_log.txt'

with open(input_filename) as f:
    input = f.read()

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

edges = [(s, c) for s in splits for c in splits[s].nbrs]

constraints = []


def addVars(iterable, basename, **kwargs):
    vars = {}
    for i in iterable:
        try:
            name = basename + '_' + '_'.join(str(x) for x in i)
        except TypeError:
            name = basename + '_' + str(i)
        vars[i] = Variable(name=name, **kwargs)
    return vars


def quicksum(iterable):

    def qs(L):
        n = len(L)
        m = n//2
        return (
            0 if n == 0 else
            L[0] if n == 1 else
            qs(L[:m]) + qs(L[m:])
        )

    return qs(list(iterable))


value = Variable(name="value")
assignments = addVars(edges, basename="a", type='binary')
discrepancies = addVars(centers, basename="c")

with timed("building split constraints"):
    # assign each split to one center
    for s in splits:
        expr = sum(assignments[s, c] for c in splits[s].nbrs)
        constraints.append(
            Constraint(expr, lb=1)
        )

with timed("building discrepancy constraints"):
    # discrepancy of each center
    for c in centers:

        constraints.extend([
            Constraint(
                - discrepancies[c]
                + centers[c].wt
                - quicksum(splits[s].wt * assignments[s, c] for s in centers[c].nbrs),
                lb=0, ub=0
            ),
            # max discrepancy
            Constraint(value - discrepancies[c], lb=0),
            Constraint(value + discrepancies[c], lb=0)
        ])

with timed("building ILP"):
    m = Model(name="m")
    m.add(constraints)
    m.objective = Objective(value, direction="min")

with timed("solving ILP"):
    assert m.optimize() == 'optimal', m.status

# for c in sorted(centers):
#     print(
#         f"center {c} assigned splits",
#         [f"{s}@{splits[s].wt}" for s in centers[c].nbrs if assignments[s, c].x == 1],
#         f". target {centers[c].wt}. discrepancy {discrepancies[c].x}.",
#     )

print("max discrepancy is", value.primal)

with open(output_filename, "w") as output:

    for s in sorted(splits):
        c = [c for c in splits[s].nbrs if assignments[s, c].primal == 1]
        assert len(c) == 1
        print(s, c[0], file=output)
