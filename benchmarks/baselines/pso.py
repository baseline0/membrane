"""Particle Swarm Optimization baseline."""

import numpy as np

from benchmarks.suites.base import BenchmarkFunction


class ParticleSwarmOptimizer:
    """Standard PSO baseline."""

    def __init__(self, pop_size: int = 30, generations: int = 1000, w: float = 0.7, c1: float = 1.5, c2: float = 1.5):
        self.pop_size = pop_size
        self.generations = generations
        self.w = w
        self.c1 = c1
        self.c2 = c2

    def optimize(self, problem: BenchmarkFunction, seed: int | None = None) -> float:
        """Run PSO on problem, return best fitness found."""
        if seed is not None:
            np.random.seed(seed)

        # Initialize particles and velocities
        particles = np.random.uniform(*problem.bounds, size=(self.pop_size, problem.dimension))
        velocities = np.random.uniform(-1, 1, size=(self.pop_size, problem.dimension))

        # Fitness evaluation
        fitness = np.array([problem(p) for p in particles])
        best_idx = np.argmin(fitness)
        global_best_pos = particles[best_idx].copy()
        global_best_fit = fitness[best_idx]
        personal_best_pos = particles.copy()
        personal_best_fit = fitness.copy()

        # PSO main loop
        for _ in range(self.generations):
            for i in range(self.pop_size):
                r1 = np.random.random(problem.dimension)
                r2 = np.random.random(problem.dimension)

                velocities[i] = (
                    self.w * velocities[i]
                    + self.c1 * r1 * (personal_best_pos[i] - particles[i])
                    + self.c2 * r2 * (global_best_pos - particles[i])
                )
                particles[i] += velocities[i]
                particles[i] = np.clip(particles[i], *problem.bounds)

                fit = problem(particles[i])
                if fit < personal_best_fit[i]:
                    personal_best_fit[i] = fit
                    personal_best_pos[i] = particles[i].copy()

                if fit < global_best_fit:
                    global_best_fit = fit
                    global_best_pos = particles[i].copy()

        return float(global_best_fit)
