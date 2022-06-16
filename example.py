from Core.GroupPopulationGenerationUtilities import randomPermutationGroup
from Core.GroupPopulationEvolver import GroupPopulationEvolver

from sage.groups.perm_gps.permgroup_named import *

import random
import math

# Example script - finding a non-Abelian group with 15 conjugacy classes which is not isomorphic to D27

if __name__ == '__main__':
    # Generate population of groups - some random, some well known
    population = [randomPermutationGroup(random.randint(4, 7), 3) for _ in range(100)] \
               + [CyclicPermutationGroup(n) for n in range(2, 10)] \
               + [AlternatingGroup(n) for n in range(3, 5)]

    # Define sigmoid function
    def sigmoid(x):
        return 1 / (1 + math.exp(-x))

    # Define score function which attains a maximum of 1 when: # of conjugacy classes is 15, group is non-Abelian and
    # group is not isomorphic to D27
    def score_function(G):
        if G.is_abelian() or G.is_isomorphic(DihedralGroup(27)):
            return 0
        else:
            return sigmoid(1 - ((len(G.conjugacy_classes()) / 15) - 1)**2)


    # Evolve 10 generations
    evolver = GroupPopulationEvolver(population, score_function)
    evolver.evolve(10)

    # Print results
    best = evolver._scores.index(max(evolver._scores))
    print("Permutation group with generators " + str(evolver.population[best].gens_small()))
    print("Number of conjugacy classes: " + str(len(evolver.population[best].conjugacy_classes())))
    print("Abelian? : " + str(evolver.population[best].is_abelian()))
    print("Isomorphic to D27? : " + str(evolver.population[best].is_isomorphic(DihedralGroup(27))))
