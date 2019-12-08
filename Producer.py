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
        # -1 to 1 uniformly with sum = 0
        random.seed(time.time())
        dividers = [random.uniform(-1,1) for i in range(n - 1)]
        right = sorted([x for x in dividers if x >= 0] + [1])
        left = sorted([x for x in dividers if x < 0] + [-1])
        result = [right[i] - right[i - 1] for i in range(1, len(right))]
        result += [left[i] - left[i + 1] for i in range(len(left) - 1)]
        result += [-sum(result)]
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
        self.last_order = delta_amount
        self.money -= delta_amount * self.model.price
        self.stocks += delta_amount

    def step(self):
        if self.wealth > 0:
            self.participating = True
            self.invest()
            self.calc_wealth()
        else:
            self.participating = False
