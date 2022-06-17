from Core.GroupPopulationGenerationUtilities import randomPermutation

import random

import sage.all
from sage.groups.perm_gps.permgroup import *


class GroupPopulationEvolver:
    def __init__(self, population, score_func, generator_crossover_p=0.4, direct_product_crossover_p=0.3,
                 drop_generator_p=0.4, add_generator_p=0.5):
        self._parameter_validity_checks(generator_crossover_p, direct_product_crossover_p, drop_generator_p,
                                        add_generator_p)

        self.population = population
        self._iterator = 9223372036854775783 % len(self.population)
        self._score_func = score_func
        self._scores = [self._score_func(p) for p in self.population]

    def _parameter_validity_checks(self, generator_crossover_p, direct_product_crossover_p, drop_generator_p,
                                   add_generator_p):
        if 1 <= generator_crossover_p or generator_crossover_p < 0 or 1 <= direct_product_crossover_p or \
                direct_product_crossover_p < 0:
            print("Crossover probabilities must be in the interval [0, 1).")
            exit(1)

        if 1 <= generator_crossover_p + direct_product_crossover_p:
            print("Crossover probabilities must sum to a value less than 1.")
            exit(1)

        if 1 <= drop_generator_p or drop_generator_p < 0 or 1 <= add_generator_p or add_generator_p < 0:
            print("Mutation probabilities must be in the interval [0, 1).")
            exit(1)

        if 1 <= drop_generator_p + add_generator_p:
            print("Mutation probabilities must sum to a value less than 1.")
            exit(1)

        self._generator_crossover_p = generator_crossover_p
        self._direct_product_crossover_p = direct_product_crossover_p
        self._drop_generator_p = drop_generator_p
        self._add_generator_p = add_generator_p

    def _drop_generator_mutation(self, G):
        generators = G.gens()
        remaining_generators = []

        g = random.randint(0, len(generators) - 1)
        for p in range(len(generators)):
            if p != g:
                remaining_generators.append(generators[p])

        return PermutationGroup(remaining_generators, canonicalize=True)

    def _add_generator_mutation(self, G):
        generators = G.gens()

        _generators = [g.cycle_tuples(singletons=True) for g in generators]
        if [()] in _generators:
            _generators.remove([()])

        def _random_permutation():
            n = max([max([max(cycle) for cycle in g]) for g in _generators])

            return PermutationGroup(_generators + [randomPermutation(n)], canonicalize=True)

        def _xyxy_permutation():
            x, y = random.sample(generators, k=2)
            g = x * y * (x**(-1)) * (y**(random.randint(1, y.order())))

            return PermutationGroup(_generators + [g.cycle_tuples(singletons=True)], canonicalize=True)

        def _xy_n_permutation():
            x, y = random.sample(generators, k=2)
            g = (x * y)**(random.randint(1, x.order() * y.order()))

            return PermutationGroup(_generators + [(g.cycle_tuples(singletons=True))], canonicalize=True)

        if len(_generators) > 1:
            mutation = random.choice([_random_permutation, _xyxy_permutation, _xy_n_permutation])
        else:
            mutation = _random_permutation

        return mutation()

    def _direct_product_crossover(self, G, H):
        return G.direct_product(H, maps=False)

    def _generating_set_crossover(self, G, H):
        generatorsG = G.gens()
        generatorsH = H.gens()

        splice_idx = random.randint(0, min(len(generatorsG) - 1, len(generatorsH) - 1))

        return PermutationGroup(generatorsG[0:splice_idx] + generatorsH[splice_idx:-1], canonicalize=True)

    def _select(self):
        candidate_idx = random.randint(0, len(self.population) - 1)

        self._iterator = self._iterator % len(self.population)
        for _ in range(len(self.population)):
            if self._scores[candidate_idx] < self._scores[self._iterator]:
                candidate_idx = self._iterator

            self._iterator = (self._iterator + 9223372036854775783) % len(self.population)

        return candidate_idx

    def evolve(self, n_iterations):
        for i in range(n_iterations):
            print("Iteration = " + str(i+1))
            children = []

            for _ in range(0, len(self.population), 2):
                p1 = self._select()
                p2 = self._select()

                crossover_select = random.random()
                if crossover_select < self._generator_crossover_p:
                    c1 = self._generating_set_crossover(self.population[p1], self.population[p2])
                    c2 = self._generating_set_crossover(self.population[p2], self.population[p1])
                elif self._generator_crossover_p <= crossover_select <= self._generator_crossover_p + \
                        self._direct_product_crossover_p:

                    c1 = self._direct_product_crossover(self.population[p1], self.population[p2])

                    if self._scores[p2] < self._scores[p1]:
                        c2 = self._direct_product_crossover(self.population[p1], self.population[p1])
                    else:
                        c2 = self._direct_product_crossover(self.population[p2], self.population[p2])
                else:
                    c1 = self.population[p1]
                    c2 = self.population[p2]

                for c in [c1, c2]:
                    mutation_select = random.random()
                    if mutation_select < self._drop_generator_p:
                        c = self._drop_generator_mutation(c)
                    elif self._drop_generator_p <= mutation_select < self._drop_generator_p + self._add_generator_p:
                        c = self._add_generator_mutation(c)

                    children.append(c)

            self._scores = [self._score_func(c) for c in children]
            self.population = children
