import statistics

import numpy as np
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.time import RandomActivation

from Producer import *
from Speculator import *
from StrategyManager import *


def compute_average_agent_wealth(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    mean_wealth = statistics.mean(agent_wealths)
    model.mean_wealth = mean_wealth
    return mean_wealth


def compute_demand(model):
    model.demand = sum([a.last_order for a in model.schedule.agents if a.last_order > 0])
    return model.demand


def compute_offer(model):
    model.offer = sum([-a.last_order for a in model.schedule.agents if a.last_order < 0])
    return model.offer


def compute_price(model):
    model.last_price = model.price
    model.price = np.exp(model.fluctuation_factor * np.tanh(np.log(model.demand / model.offer) / model.fluctuation_factor))
    return model.price

def compute_producer_participation_rate(model):
    participation_count = sum([1 for a in model.schedule.agents if a.participating and isinstance(a, Producer)])
    return participation_count/model.num_producers

def compute_speculator_participation_rate(model):
    participation_count = sum([1 for a in model.schedule.agents if a.participating and isinstance(a, Speculator)])
    return participation_count/model.num_speculators



class MoneyModel(Model):
    def __init__(self, Ns, Np, influx, width, height, fluctuation_factor,
                 amplitude, producer_money, bias_factor, memory_size,
                 speculator_money, prudent_factor):
        super().__init__()
        self.demand = 1
        self.offer = 1
        self.num_speculators = Ns
        self.num_producers = Np
        self.num_agents = Ns + Np
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.last_price = 0
        self.price = 1
        self.fluctuation_factor = fluctuation_factor
        self.demand_ratio = 1
        self.influx = influx
        self.amplitude = amplitude
        self.producer_money = producer_money
        self.bias_factor = bias_factor
        self.speculator_money = speculator_money
        self.prudent_factor = prudent_factor
        self.memory_size = memory_size
        self.stategy_manager = StrategyManager(model=self, memory_size=memory_size)
        self.mean_wealth = 1
        self.memory = "0" * memory_size

        # Create Producers
        for i in range(self.num_producers):
            p = Producer(unique_id=i, model=self, money=producer_money, bias_factor=bias_factor, amplitude=amplitude)
            self.schedule.add(p)
        # Create Speculators
        for i in range(self.num_producers + 1, self.num_producers + self.num_speculators + 1):
            s = Speculator(unique_id=i, model=self, money=self.speculator_money,
                           prudent_factor=self.prudent_factor, strategy_manager=self.stategy_manager,
                           memory_size=self.memory_size)
            self.schedule.add(s)
        # Put agents to grid
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                if x*(self.grid.width) + y < len(self.schedule.agents):
                    self.grid.place_agent(self.schedule.agents[x*(self.grid.width) + y], (x, y))
                else:
                    break

        self.datacollector = DataCollector(
            model_reporters={"Average Agent Wealth": compute_average_agent_wealth,
                             "Price": compute_price,
                             "Offer": compute_offer,
                             "Producer Participation Rate": compute_producer_participation_rate,
                             "Speculator Participation Rate": compute_speculator_participation_rate,
                             "Demand": compute_demand},
            agent_reporters={"Wealth": "wealth"})

    def update_memory(self):
        # the paper didn't consider when the price doesn't change
        # 0 for increase 1 for decrease
        price_change = "0" if self.last_price < self.price else "1"
        self.memory = self.memory[1:] + str()

    def step(self):

        # Calculate amount of the commodity, attempted to buy by producers (Eq. (1)) and speculators (Eq. (2)).
        self.schedule.step()
        # Calculate demand and offer and from them the new price, according to (3) and (4).
        # Calculate new values of capital, stock and money according to (5), (6), and (7).
        self.datacollector.collect(self)
        # update strategy scores
        self.stategy_manager.update_strategy_scores()


        # The following are performed periodically
        # replace poorly performing speculators
        if self.schedule.steps % 5 == 0:
            poorest_speculator = None
            poorest_wealth = math.inf
            for agent in self.schedule.agents:
                if isinstance(agent, Speculator):
                    if agent.wealth < poorest_wealth:
                        poorest_wealth = agent.wealth
                        poorest_speculator = agent
            poorest_speculator.pick_new_strategy()
        # randomize speculator strategy
        if self.schedule.steps % 57 == 0:
            randomize_speculator_id = math.floor(random.uniform(0, self.num_speculators))
            count = 0
            for agent in self.schedule.agents:
                if isinstance(agent, Speculator):
                    if count == randomize_speculator_id:
                        agent.randomize_strategy()
                        break
                    count += 1
        # influx of external money
        if self.schedule.steps % 120 == 0:
            amount = self.influx * self.num_producers / sum(1 for a in self.schedule.agents if a.participating)
            for agent in self.schedule.agents:
                if isinstance(agent, Producer) and agent.participating:
                    agent.influx(amount)



