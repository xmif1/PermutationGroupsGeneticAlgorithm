import random

import sage.all
from sage.groups.perm_gps.permgroup import *


def randomPermutation(n):
    max_cycles = random.randint(1, n)
    S = set(range(1, n + 1))

    cycles = []
    for _ in range(max_cycles):
        if 0 < len(S):
            cycle = random.sample(S, k=random.randint(1, len(S)))
            cycles.append(tuple(cycle))

            S = S - set(cycle)

    return cycles


def randomPermutationGroup(n, max_generators):
    generators = []
    n_generators = random.randint(1, max_generators)

    for _ in range(n_generators):
        generators.append(randomPermutation(n))

    return PermutationGroup(generators, canonicalize=True)

