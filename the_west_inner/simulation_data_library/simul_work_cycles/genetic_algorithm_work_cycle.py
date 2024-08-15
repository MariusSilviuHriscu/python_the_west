import random
from typing import List, Optional

from the_west_inner.simulation_data_library.simul_work_cycles.work_cycle_simul import SimulatorWorkCycle
from the_west_inner.simulation_data_library.simul_work_cycles.work_cycle_simul_data import WorkCycleJobSimul, WorkCycleSimul

class WorkCycleGeneticAlgorithm:
    def __init__(self, 
                 work_cycle_jobs: List[WorkCycleJobSimul], 
                 simulator: SimulatorWorkCycle, 
                 population_size: int = 500, 
                 generations: int = 100, 
                 mutation_rate: float = 0.05, 
                 max_works: Optional[int] = None):
        self.work_cycle_jobs = work_cycle_jobs
        self.simulator = simulator
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.max_works = max_works

    def initialize_population(self) -> List[WorkCycleSimul]:
        population = []
        for _ in range(self.population_size):
            individual = self._create_individual()
            while not individual.is_valid_cycle():
                individual = self._create_individual()
            population.append(individual)
        return population

    def _create_individual(self) -> WorkCycleSimul:
        num_works = self.max_works if self.max_works else random.randint(1, len(self.work_cycle_jobs))
        selected_jobs = random.sample(self.work_cycle_jobs, num_works)
        return WorkCycleSimul(work_data_list=selected_jobs)

    def evaluate_fitness(self, individual: WorkCycleSimul) -> float:
        simulation = self.simulator.simulate(individual)
        if simulation.elapsed_time == 0:  # Prevent division by zero
            return 0
        return simulation.exp_gained / simulation.elapsed_time

    def select_parents(self, population: List[WorkCycleSimul], fitness_scores: List[float]) -> List[WorkCycleSimul]:
        selected = random.choices(population, weights=fitness_scores, k=2)
        return selected

    def crossover(self, parent1: WorkCycleSimul, parent2: WorkCycleSimul) -> WorkCycleSimul:
        split_point = random.randint(1, min(len(parent1.work_data_list), len(parent2.work_data_list)) - 1)
        child_work_data = parent1.work_data_list[:split_point] + parent2.work_data_list[split_point:]
        child = WorkCycleSimul(work_data_list=child_work_data)
        while not child.is_valid_cycle():
            child = self._create_individual()  # If invalid, reinitialize
        return child

    def mutate(self, individual: WorkCycleSimul) -> WorkCycleSimul:
        if random.random() < self.mutation_rate:
            mutation_index = random.randint(0, len(individual.work_data_list) - 1)
            individual.work_data_list[mutation_index] = random.choice(self.work_cycle_jobs)
            while not individual.is_valid_cycle():
                individual.work_data_list[mutation_index] = random.choice(self.work_cycle_jobs)
        return individual

    def evolve_population(self, population: List[WorkCycleSimul]) -> List[WorkCycleSimul]:
        new_population = []
        fitness_scores = [self.evaluate_fitness(individual) for individual in population]
        for _ in range(self.population_size):
            parent1, parent2 = self.select_parents(population, fitness_scores)
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            new_population.append(child)
        return new_population

    def run(self) -> WorkCycleSimul:
        population = self.initialize_population()
        best_individual = None
        best_fitness = 0
        for generation in range(self.generations):
            population = self.evolve_population(population)
            current_best = max(population, key=lambda ind: self.evaluate_fitness(ind))
            current_best_fitness = self.evaluate_fitness(current_best)
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                best_individual = current_best
            print(f"Generation {generation}: Best Fitness = {best_fitness}")
        return best_individual