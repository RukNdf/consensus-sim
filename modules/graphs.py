import matplotlib.pyplot as plt

def graph(blocktimes, nodes):
    times = blocktimes[:-1]
    latencies = [blocktimes[i+1]-blocktimes[i] for i in range(len(times))]
    plt.plot(
        times,
        latencies,
        marker="o",
        linewidth=1,
        markersize=3,
    )
    
    n = len(nodes)
    indexes = [i for i in range(0,len(times),n)]
    averagex = [times[i] for i in indexes]
    averagey = [0] + [sum(latencies[i-n:i])/n for i in indexes[1:]]
    averagey[0] = averagey[1]
    
    plt.plot(
        averagex,
        averagey,
        linewidth=1,
        color='red' ,
    )

    plt.xlabel("Block proposal time (ms)")
    plt.ylabel("Time to commit block (ms)")
    plt.title("Block Proposal Time vs. Commit Time")

    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    #plt.savefig(filename, dpi=150)
    plt.show()