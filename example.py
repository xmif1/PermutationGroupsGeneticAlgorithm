from Core.GroupPopulationGenerationUtilities import randomPermutationGroup
from Core.GroupPopulationEvolver import GroupPopulationEvolver

from sage.groups.perm_gps.permgroup_named import *
from sage.groups.perm_gps.permgroup import *

import numpy as np
import random
import math

# Example script - finding a non-Abelian group with 15 conjugacy classes which is not isomorphic to D27, S7, GL(2, 4)
# or C5 x S3.

if __name__ == '__main__':
    # Generate population of groups - some random, some well known
    population = [randomPermutationGroup(random.randint(3, 8), 5) for _ in range(500)]

    GL_2_4 = PermutationGroup([[(1, 7, 5, 4, 8), (2, 3, 6)], [(1, 8, 5, 7, 4)]])
    C5xS3 = PermutationGroup([[(1, 4, 5)], [(1, 5), (2, 6, 7, 8, 3)]])

    # Define sigmoid function
    def sigmoid(x):
        return 1 / (1 + math.exp(-x))

    # Define score function which attains a maximum of 1 when: # of conjugacy classes is 15, group is non-Abelian and
    # group is not isomorphic to D27, S7, GL(2, 4) or C5 x S3
    def score_function(G):
        if G.is_abelian() or G.is_isomorphic(DihedralGroup(27)) or G.is_isomorphic(SymmetricGroup(7))\
                or G.is_isomorphic(GL_2_4) or G.is_isomorphic(C5xS3):
            return -np.Inf
        else:
            n_conjugacy_classes = len(G.conjugacy_classes())
            if n_conjugacy_classes >= 150:
                return -np.Inf
            else:
                return sigmoid(1 - ((n_conjugacy_classes / 15) - 1)**2)


    # Evolve 10 generations
    evolver = GroupPopulationEvolver(population, score_function)
    evolver.evolve(10)

    # Print results
    best_score = max(evolver._scores)
    best_pgrp = evolver.population[evolver._scores.index(best_score)]
    print("Maximum score: " + str(((1 + math.e) / math.e) * best_score))
    print("Permutation group " + best_pgrp.structure_description() + " with generators " + str(best_pgrp.gens_small()))
