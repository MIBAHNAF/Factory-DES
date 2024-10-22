import simpy
import numpy as np

def factory_run(env,repairers, spares):
    global cost
    cost = 0.0
    for i in range(50):
        env.process(operate_machine(env, repairers, spares))
    while True:
        cost += 3.75*8*repairers.capacity+30*spares.capacity
        yield env.timeout(8.0)

def operate_machine(env, repairers, spares):
    global cost
    while True:
        yield env.timeout(generate_time_to_failure())
        t_broken = env.now
        print('%7.4f Machine broke down' % t_broken)
        env.process(repair_machine(env, repairers, spares))
        yield spares.get(1)
        t_replaced = env.now
        print('%7.4f Spares available, machine replaced' % t_replaced)
        cost += 20*(t_replaced-t_broken)

def repair_machine(env, repairers, spares):
    with repairers.request() as request:
        yield request
        yield env.timeout(generate_repair_time())
        yield spares.put(1)

def generate_time_to_failure():
    return np.random.uniform(132, 182)

def generate_repair_time():
    return np.random.uniform(4, 10)

obs_times = []
obs_costs = []
obs_spares = []
def observe(env, spares):
    while True:
        obs_times.append(env.now)
        obs_costs.append(cost)
        obs_spares.append(spares.level)
        yield env.timeout(1.0)

np.random.seed(0)

env = simpy.Environment()
repairers = simpy.Resource(env, capacity=3)
spares = simpy.Container(env, init=20, capacity=20)
env.process(factory_run(env, repairers, spares))
env.process(observe(env, spares))
env.run(until=8*5*52)

import matplotlib.pyplot as plt
plt.figure()
plt.step(obs_times, obs_spares, where='post')
plt.xlabel('Time (hours)')
plt.ylabel('Spares level')

plt.figure()
plt.step(obs_times, obs_costs, where='post')
plt.xlabel('Time (hours)')
plt.ylabel('Cost incurred')



