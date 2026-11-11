import simpy

from modules.consensus import *
from modules.topology import *
from modules.graphs import *    


# Define the behavior of the leader selection function
def rotativeLeader(network, _):
    next = network.leader[-1] + 1 
    if next >= len(nodes):
        next = 0
    network.leader += [next]


# Contador global
counter = 1      
# Sequencias de lider 
pior = [0, 7, 2, 8, 6, 10, 1, 9, 3, 12, 5, 4, 11]
melhor = [0, 4, 10, 11, 8, 12, 9, 2, 6, 7, 3, 1, 5]
padrao = [i for i in range(13)]
# Opcao 
rota = melhor
# Funcao de lider 
def ordem(network, _):
    global counter
    next = rota[counter]
    counter += 1
    if counter >= len(rota):
        counter = 0
    network.leader += [next]



# Process latency matrix
nodes, latency = read_latency_matrix('lat/latency.csv') 
# Define how many blocks the simulations runs for 
MAXBLOCK = len(nodes)+2
# Select leader behavior function 
leaderFunction = ordem


# Start simulation 
env = simpy.Environment()
sim = Consensus(env, leaderFunction, nodes, latency, MAXBLOCK)
sim.start()
env.run()


# Graph result 
graph(sim.blocktimes, nodes)
#
# Graph plots leader-to-leader latency.
#
# Y position shows the time it took from the leader of height h to propose
# to the leader of h+1 to commit that same block. 
# The higher a point is, the more latency that consensus experienced. 
# Lower points are better in that consensus was faster and the next
# block started sooner. 
#
# X position shows the point in time where a proposal happened. 
# points closer together in the X axis implies on a quicker sucession 
# of blocks. Points farther apart implies in more block-to-block time. 
# This metric is proportional to the Y values. 
# The last point in the X axis marks when the experiment ended
# i.e. the total time to commit all the MAXBLOCK blocks. 
# 
# The red bar plots average per n blocks. If leader selection is
# rotative, the bar will stay constant as the same sequence of 
# proposers happen. If leader selection changes or is irregular 
# the bar will change accordingly. 
