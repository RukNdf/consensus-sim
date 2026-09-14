import csv
from modules.consensus import *

def read_latency_matrix(filename = 'lat/latency.csv'): 
    with open(filename, "r", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    nodelist = [x.strip() for x in rows[0][1:]]
    nodes = []
    nodenum = len(nodelist)
    for i in range(nodenum):
        nodes += [Node(i)]
        
    latency = [[[-1] for i in range(nodenum)] for i in range(nodenum)]

    for row in rows[1:]:
        if not row:
            continue
        source = nodelist.index(row[0].strip())
        for dest, value in enumerate(row[1:]):
            latency[source][dest] = float(value)

    return nodes, latency