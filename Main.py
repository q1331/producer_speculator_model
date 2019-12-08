from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule

from MoneyModel import *


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": agent.wealth}

    if agent.participating:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
    else:
        portrayal["Color"] = "black"
        portrayal["Layer"] = 1
        portrayal["r"] = agent.wealth / 5
    return portrayal


gird_height = 50
gird_width = 50
canvas_height = 500
canvas_width = 500
grid = CanvasGrid(agent_portrayal, grid_height=gird_height, grid_width=gird_width,
                  canvas_height=canvas_height, canvas_width=canvas_width)
chart = ChartModule([{"Label": "Average Agent Wealth",
                      "Color": "Black"}],
                    data_collector_name='datacollector')
price_chart = ChartModule([{"Label": "Price",
                            "Color": "black"}],
                          data_collector_name='datacollector')
offer_chart = ChartModule([{"Label": "Offer",
                            "Color": "green"}],
                          data_collector_name='datacollector')
demand_chart = ChartModule([{"Label": "Demand",
                             "Color": "red"}],
                           data_collector_name='datacollector')

server = ModularServer(MoneyModel,
                       [grid, chart, price_chart, offer_chart, demand_chart],
                       "Money Model",
                       {"Ns": 1000, "Np": 50, "influx": 0.001, "fluctuation_factor": 0.02,
                        "amplitude": 0.01, "producer_money": 1, "bias_factor": 0.01, "memory_size": 10,
                        "speculator_money": 1, "prudent_factor": 0.001, "width": gird_width, "height": gird_height})
server.port = 8521
server.launch()
