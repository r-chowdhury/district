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
            self.pop = 0
            self.area = 0
            self.nbrs = []

        def add_nbr(self, *others):
            self.nbrs.extend(others)

    class Edge:

        def __init__(self):
            self.pop = 0
            self.area = 0

    districts = defaultdict(lambda: Node())
    blocks = defaultdict(lambda: Node())
    edges = defaultdict(lambda: Edge())
    dependencies = []

    for line in input:
        # <block ID> (<center/district ID> <population> <area of intersection> <dependee>)*
        # where <dependee> is the block ID of another block if assigning the current block
        # to a given center requires that the other block also be assigned to that center.
        # If there is no dependee, the value of <dependee> will be the block ID of the current block.
        if line.strip():
            line = [eval(x) for x in line.split()]
            # if len(line) % 3 != 1: continue
            assert len(line) % 4 == 1, line
            b, *line = line
            for d, pop, area, dependee_block in (
                line[3 * i : 3 * (i + 1)] for i in range(int(len(line) / 3))
            ):
                assert (b, d) not in edges
                blocks[b].add_nbr(d)
                districts[d].add_nbr(b)
                for x in blocks[b], districts[d], edges[b, d]:
                    x.pop += pop
                    x.area += area
                if dependee_block != b:
                    dependencies.add(((b, d), (dependee_block, d)))

    return blocks, districts, edges, dependencies


def pulp_assign(solver, input):

    # https://pythonhosted.org/PuLP/index.html
    # sudo port install py36-pyparsing
    # pip install --upgrade --user pulp   # (depends on pyparsing)

    import pulp

    print_log("computing assignment using pulp, solver", solver)

    solvers = {
        "gurobi": pulp.solvers.GUROBI,
        "glpk": pulp.solvers.GLPK,
        "cbc": pulp.solvers.PULP_CBC_CMD,
    }

    try:
        solver = solvers[solver]()
    except KeyError:
        print_log("error: unknown pulp solver", solver)
        print_log("known solvers:", ", ".join(solvers.keys()))
        print_log(
            "available solvers:",
            ", ".join(n for n, s in solvers.items() if s().available()),
        )
        sys.exit(-1)

    if not solver.available():
        print_log("error: solver not available")
        print_log(
            "available solvers:",
            ", ".join(n for n, s in solvers.items() if s().available()),
        )
        sys.exit(-1)

    blocks, districts, edges, dependencies = input_boundary_districts(input)

    constraints = []

    value = pulp.LpVariable("value")
    max_discrepancy = pulp.LpVariable("max_discrepancy")
    refugee_blocks = pulp.LpVariable("refugee_blocks")
    assignments = pulp.LpVariable.dicts(
        "a", edges.keys(), lowBound=0, upBound=1, cat=pulp.LpInteger
    )
    discrepancies = pulp.LpVariable.dict("d", districts)

    with timed("building split constraints"):
        # assign each split to one center
        for b in blocks:
            constraints.append(sum(assignments[b, d] for d in blocks[b].nbrs) == 1)

    with timed("building discrepancy constraints"):
        # discrepancy of each center
        for d in districts:

            constraints.extend([
                -discrepancies[d]
                + districts[d].pop
                - pulp.lpSum(
                    blocks[b].pop * assignments[b, d] for b in districts[d].nbrs
                )
                == 0,
                # max discrepancy
                max_discrepancy - discrepancies[d] >= 0,
                max_discrepancy + discrepancies[d] >= 0,
            ])

    with timed("building refugee_blocks constraint"):
        preferred_districts = {}
        for b in blocks:
            d = max(blocks[b].nbrs, key=lambda d: edges[b, d].area)
            if edges[b, d].area >= 0.666 * blocks[b].area:
                preferred_districts[b] = d

        constraints.extend([
            refugee_blocks
            == pulp.lpSum(
                assignments[b, d]
                for (b, d) in edges
                if b in preferred_districts and preferred_districts[b] != d
            ),
            # ILP objective
            value == max_discrepancy + 1.0 * refugee_blocks,
        ])

    with timed("building dependency constraints"):
        constraints.extend(
            assignments[b, d1] <= assignments[dependee_block, d2]
            for ((b, d1), (dependee_block, d2)) in dependencies
        )

    with timed("building ILP"):
        m = pulp.LpProblem("m", pulp.LpMinimize)
        m += value
        for c in constraints:
            m += c

    with timed("solving ILP"):
        tmp, sys.stdout = sys.stdout, log
        try:
            m.solve(solver)
        finally:
            sys.stdout = tmp

    print_log("max discrepancy:", max_discrepancy.value())
    print_log(f"number of refugee blocks: {refugee_blocks.value()}"
              f"(of {len(preferred_districts)} with preferred_districts)")

    assignment = {}

    for b in sorted(blocks):
        d = [d for d in blocks[b].nbrs if assignments[b, d].value() == 1]
        assert len(d) == 1
        assignment[b] = d[0]

    check_assignment(blocks, districts, assignment, max_discrepancy.value())

    return assignment


def check_assignment(blocks, districts, assignment, discrepancy):
    assert set(blocks.keys()) == set(assignment.keys())

    pops = defaultdict(lambda: 0)
    for b in blocks:
        pops[assignment[b]] += blocks[b].pop

    assert set(districts.keys()).issubset(set(pops.keys()))

    discrepancy2 = max(abs(districts[d].pop - pops[d]) for d in districts)

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
        for b in sorted(assignment.keys()):
            print(b, assignment[b], file=output)

    if out_filename == "-":
        output_assignment(sys.stdout)
    else:
        with open(out_filename, "w") as output:
            output_assignment(output)

    if log not in (sys.stderr, sys.stdout):
        log.close()
