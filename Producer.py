from mesa import Agent
import random
import time
import math
import statistics


class Producer(Agent):
    def __init__(self, unique_id, model, amplitude, money, bias_factor):
        super().__init__(unique_id, model)
        self.wealth = money
        self.period = self.gen_period()
        self.time_scale = self.gen_time_scale()
        self.amplitude = amplitude
        self.bias_factor = bias_factor
        self.quench_factor = self.gen_quench_factor(self.period)
        self.last_order = 0
        self.money = money
        self.stocks = 0
        self.participating = False

    def gen_quench_factor(self, n):
        # TODO: make this right
        total = 1
        dividers = sorted([random.uniform(0, total) for i in range(n - 1)])
        result = [a - b for a, b in zip(dividers + [total], [0] + dividers)]
        mean = statistics.mean(result)
        result = list(map(lambda x: x if x > mean else -x, result))
        return result

    def gen_period(self):
        random.seed(time.time())
        return random.randint(2, 6)

    def gen_time_scale(self):
        random.seed(time.time())
        return random.randint(7, 10)

    def calc_wealth(self):
        self.wealth = self.money + self.stocks * self.model.price

    def influx(self, amount):
        self.money += amount
        self.wealth += amount

    def invest(self):
        delta_amount = self.amplitude * (
                    self.quench_factor[(self.model.schedule.steps // self.time_scale) % self.period] -
                    self.bias_factor * math.log(self.model.price / self.model.mean_wealth))
        if self.model.demand > self.model.offer and delta_amount > 0:
            delta_amount = delta_amount * self.model.offer / self.model.demand
        if self.model.demand < self.model.offer and delta_amount < 0:
            delta_amount = delta_amount * self.model.demand / self.model.offer
        self.money -= delta_amount * self.model.price
        self.stocks += delta_amount
        self.last_order = delta_amount

    def step(self):
        if self.wealth > 0:
            self.participating = True
            self.invest()
            self.calc_wealth()
        else:
            self.participating = False
