"""Genetic Algorithm baseline using DEAP."""

import numpy as np
from deap import algorithms, base, creator, tools

from benchmarks.suites.base import BenchmarkFunction


class GeneticAlgorithm:
    """Standard genetic algorithm baseline."""

    def __init__(self, pop_size: int = 100, generations: int = 1000, cxpb: float = 0.7, mutpb: float = 0.2):
        self.pop_size = pop_size
        self.generations = generations
        self.cxpb = cxpb
        self.mutpb = mutpb

    def optimize(self, problem: BenchmarkFunction, seed: int | None = None) -> float:
        """Run GA on problem, return best fitness found."""
        if seed is not None:
            import random

            random.seed(seed)
            np.random.seed(seed)

        if hasattr(creator, "FitnessMin"):
            del creator.FitnessMin
        if hasattr(creator, "Individual"):
            del creator.Individual

        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        def clip_individual(ind):
            for i in range(len(ind)):
                ind[i] = np.clip(ind[i], *problem.bounds)
            return ind

        def mate_clipped(ind1, ind2):
            tools.cxBlend(ind1, ind2, alpha=0.5)
            clip_individual(ind1)
            clip_individual(ind2)
            return ind1, ind2

        def mutate_clipped(individual):
            tools.mutGaussian(individual, mu=0, sigma=1, indpb=0.2)
            clip_individual(individual)
            return (individual,)

        toolbox = base.Toolbox()
        toolbox.register("attr_float", np.random.uniform, *problem.bounds)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=problem.dimension)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", lambda x: (problem(np.array(x)),))
        toolbox.register("mate", mate_clipped)
        toolbox.register("mutate", mutate_clipped)
        toolbox.register("select", tools.selBest)

        pop = toolbox.population(n=self.pop_size)
        pop, _ = algorithms.eaSimple(
            pop, toolbox, cxpb=self.cxpb, mutpb=self.mutpb, ngen=self.generations, verbose=False
        )

        best_fitness = min([ind.fitness.values[0] for ind in pop])
        return float(best_fitness)
