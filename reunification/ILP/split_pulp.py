#!/usr/bin/env python3

import sys
from collections import defaultdict
from contextlib import contextmanager
from timeit import default_timer as timer

log = None


def print_log(*args, **kwargs):
    global log
    print(*args, **kwargs, file=log)


@contextmanager
def timed(before):
    print_log(before, end="", flush=True)
    start = timer()
    yield
    stop = timer()
    print_log(f" ({stop-start:.2g}s)", flush=True)


def input_boundary_districts(input):

    class Node:

        def __init__(self):
            self.wt = 0
            self.nbrs = []

        def add_nbr(self, *others):
            self.nbrs.extend(others)

    centers = defaultdict(lambda: Node())
    splits = defaultdict(lambda: Node())

    for line in input:
        if line.strip():
            line = [int(x) for x in line.split()]
            assert len(line) % 2 == 1
            s, *line = line
            for c, n in (line[2 * i : 2 * i + 2] for i in range(int(len(line) / 2))):
                splits[s].wt += n
                centers[c].wt += n
                splits[s].add_nbr(c)
                centers[c].add_nbr(s)

    edges = [(s, c) for s in splits for c in splits[s].nbrs]

    return splits, centers, edges


def pulp_assign(solver, input):

    # https://pythonhosted.org/PuLP/index.html
    # sudo port install py36-pyparsing
    # pip install --upgrade --user pulp   # (depends on pyparsing)

    import pulp

    print_log("computing assignment using pulp, solver", solver)

    solvers = {"gurobi": pulp.solvers.GUROBI, "glpk": pulp.solvers.GLPK}

    try:
        solver = solvers[solver]()
    except KeyError:
        print_log("error: unknown pulp solver", solver)
        sys.exit(-1)

    if not solver.available():
        print_log("error: solver not available")
        sys.exit(-1)

    splits, centers, edges = input_boundary_districts(input)

    constraints = []

    value = pulp.LpVariable("value")
    assignments = pulp.LpVariable.dicts(
        "a", edges, lowBound=0, upBound=1, cat=pulp.LpInteger
    )
    discrepancies = pulp.LpVariable.dict("d", centers)

    with timed("building split constraints"):
        # assign each split to one center
        for s in splits:
            constraints.append(sum(assignments[s, c] for c in splits[s].nbrs) == 1)

    with timed("building discrepancy constraints"):
        # discrepancy of each center
        for c in centers:

            constraints.extend(
                [
                    -discrepancies[c]
                    + centers[c].wt
                    - pulp.lpSum(
                        splits[s].wt * assignments[s, c] for s in centers[c].nbrs
                    )
                    == 0,
                    # max discrepancy
                    value - discrepancies[c] >= 0,
                    value + discrepancies[c] >= 0,
                ]
            )

    with timed("building ILP"):
        m = pulp.LpProblem("m", pulp.LpMinimize)
        m += value
        for c in constraints:
            m += c

    with timed("solving ILP"):
        tmp, sys.stdout = sys.stdout, log
        m.solve(solver)
        sys.stdout = tmp

    discrepancy = value.value()

    print_log("max discrepancy", discrepancy)

    assignment = {}

    for s in sorted(splits):
        c = [c for c in splits[s].nbrs if assignments[s, c].value() == 1]
        assert len(c) == 1
        assignment[s] = c[0]

    check_assignment(splits, centers, assignment, discrepancy)

    return assignment


def check_assignment(splits, centers, assignment, discrepancy):
    assert set(splits.keys()) == set(assignment.keys())

    weights = defaultdict(lambda: 0)
    for s in splits:
        weights[assignment[s]] += splits[s].wt

    assert set(centers.keys()).issubset(set(weights.keys()))

    discrepancy2 = max(abs(centers[c].wt - weights[c]) for c in centers)

    assert discrepancy2 == discrepancy


if __name__ == "__main__":

    try:
        cmd, *args = sys.argv
        solver, in_filename, out_filename, log_filename = args

    except ValueError:
        print(
            f"usage: {cmd} solver in_filename out_filename log_filename",
            file=sys.stderr,
        )
        sys.exit(-1)

    if solver == "-":
        solver = "gurobi"

    if log_filename == "-":
        log = sys.stderr if out_filename == "-" else sys.stdout
    else:
        log = open(log_filename, "w")

    if in_filename == "-":
        assignment = pulp_assign(solver, sys.stdin)
    else:
        with open(in_filename) as input:
            assignment = pulp_assign(solver, input)

    def output_assignment(output):
        for s in sorted(assignment.keys()):
            print(s, assignment[s], file=output)

    if out_filename == "-":
        output_assignment(sys.stdout)
    else:
        with open(out_filename, "w") as output:
            output_assignment(output)

    if log not in (sys.stderr, sys.stdout):
        log.close()
