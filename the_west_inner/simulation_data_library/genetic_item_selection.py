import random
import numba



from the_west_inner.simulation_data_library.simul_items import Item_model_list
from the_west_inner.simulation_data_library.simul_equipment import Equipment_simul
from the_west_inner.simulation_data_library.simul_sets import Item_set_list
from the_west_inner.simulation_data_library.simul_equip_fitnes import SimulFitnessRuleSet
from the_west_inner.simulation_data_library.simul_permutation_data import EquipmentPermutationData
from the_west_inner.simulation_data_library.simul_data_loader import Simulation_data_loader




class GeneticAlgorithm:
    def __init__(self, item_model_list: Item_model_list, set_model_list: Item_set_list, equipment_simul: Equipment_simul, fitness_rule_set: SimulFitnessRuleSet, population_size=50, generations=100, mutation_rate=0.01):
        self.item_model_list = item_model_list
        self.set_model_list = set_model_list
        self.equipment_simul = equipment_simul
        self.fitness_rule_set = fitness_rule_set
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

    def initialize_population(self):
        population = []
        item_type_dict = self.item_model_list.get_item_dict()
        item_types = list(item_type_dict.keys())
        for _ in range(self.population_size):
            individual = {item_type: random.choice(item_type_dict[item_type]) for item_type in item_types}
            population.append(individual)
        return population

    def fitness(self, individual):
        self.equipment_simul.empty()
        for item_type, item in individual.items():
            self.equipment_simul.replace_item(replacement_item=item)
        equipment_data = EquipmentPermutationData(
            **self.equipment_simul.create_status_dict(),
            **{"permutation": individual}
        )
        return self.fitness_rule_set.get_fitness_result(equipment_data)
    

    def select(self, population, fitnesses):
        selected = []
        for _ in range(len(population)):
            index1, index2 = random.sample(range(len(population)), 2)
            fitness1 = fitnesses[index1]
            fitness2 = fitnesses[index2]
            selected.append(population[index1] if fitness1 > fitness2 else population[index2])
        return selected



    def crossover(self, parent1, parent2):
        child = {}
        for key in parent1.keys():
            child[key] = random.choice([parent1[key], parent2[key]])
        return child

    def mutate(self, individual):
        if random.random() < self.mutation_rate:
            item_type_dict = self.item_model_list.get_item_dict()
            item_type = random.choice(list(individual.keys()))
            individual[item_type] = random.choice(item_type_dict[item_type])
        return individual

    def run(self):
        jit_fitness = numba.jit()(self.fitness)
        population = self.initialize_population()
        best_individual = None
        best_fitness = self.fitness_rule_set.generate_empty_result()

        for generation in range(self.generations):
            fitnesses = [jit_fitness(individual) for individual in population]
            population = self.select(population, fitnesses)
            next_population = []
            for i in range(0, len(population), 2):
                parent1 = population[i]
                parent2 = population[(i+1) % len(population)]
                child1 = self.crossover(parent1, parent2)
                child2 = self.crossover(parent1, parent2)
                next_population.extend([self.mutate(child1), self.mutate(child2)])
            population = next_population

            for individual in population:
                current_fitness = jit_fitness(individual)
                if current_fitness > best_fitness:
                    best_fitness = current_fitness
                    best_individual = individual

        return EquipmentPermutationData(
            **self.equipment_simul.create_status_dict(),
            **{"permutation": best_individual}#, "fitness": best_fitness}
        )

# Example usage
def run_genetic_algorithm_simulation(game_data , fitness_rule_set : SimulFitnessRuleSet):
    loader = Simulation_data_loader(game_data)
    item_model_list = loader.assemble_item_model_list_from_game_data()
    set_model_list = loader.assemble_item_set_model_list_from_game_data()
    equipment_simul = loader.assemble_simul_equipment_from_game_data()
    
    
    
    ga = GeneticAlgorithm(
        item_model_list=item_model_list,
        set_model_list=set_model_list,
        equipment_simul=equipment_simul,
        fitness_rule_set=fitness_rule_set,
        population_size=1000,
        generations=1000,
        mutation_rate=0.03
    )

    best_equipment = ga.run()
    return best_equipment