# Safely adds non-duplicated values to a dictionary
def addTo(dictionary, key, value):
    if key not in dictionary:
        dictionary[key] = [value]
    else:
        if value not in dictionary[key]:
            dictionary[key] += [value]


#
# Node object
#
class Node:    
    def __init__(self, i):
        # Node's id
        self.i = i
        # Node's current height
        self.height = 1
        # Node's local prevote list
        self.prevotes = {}
        # Node's local precommit list 
        self.precommits = {}
        # Node is awaiting prevote for a block
        self.awaitingPrevote = True
        # Node is awaiting precommit for a block
        self.awaitingPrecom = False


#
# Consensus simulation 
#
class Consensus:
    # Initial state
    def __init__(self, env, nextLeader, nodes, latency, MAXBLOCK):
        # Past and current leaders 
        self.leader = [-1,0]
        # Simpy environment 
        self.env = env
        # Next leader function
        self.nextLeader = nextLeader
        # Consensus block times, used for the graphs
        self.blocktimes = [0]
        # Topology nodes
        self.nodes = nodes
        # Topology latencies
        self.latency = latency
        # Byzantine quorum
        self.quorum = int(len(nodes)*2/3)+1
        # Simulation block limit 
        self.MAXBLOCK = MAXBLOCK
        
    # Send the initial proposal and start the experiment 
    def start(self):
        # Initial height
        height = 1
        # Get leader
        src = self.leader[height]
        # Precalculate next leader 
        self.nextLeader(self, self.nodes[0])
        # Send proposal 
        print(f"{self.env.now}: {src} : Proposing {height}")
        broadcast = [n for n in range(len(self.nodes)) if n != src]
        for dst in broadcast:
            self.env.process(self.send(src, dst, 'proposal', height))

    # Message simulation 
    def send(self, src, dst, mtype, message):
        yield self.env.timeout(self.latency[src][dst])
        # Process at the receiving end
        node = dst
        # Nodes this node will broadcast to 
        broadcast = [n for n in range(len(self.nodes)) if n != node]
        #
        # Node has received proposal 
        if mtype == 'proposal':
            self.receiveProposal(src, node, broadcast, message)
        if mtype == 'prevote':
            self.receivePrevote(src, node, broadcast, message)
        if mtype == 'precommit':
            self.receivePrecommit(src, node, broadcast, message)
                            
    # Node has received a proposal 
    def receiveProposal(self, src, nodeID, broadcast, message):
        # Extract vars from message 
        height = message
        # Get node object 
        node = self.nodes[nodeID]
        print(f"{self.env.now}: {src} -> {nodeID}: receive proposal")
        # Treat proposal as an implicit prevote for the proposer's block, 
        # store it in local prevotes list 
        addTo(node.prevotes, height, src)
        # Add own vote to prevote list (we assume the block is always valid)
        node.prevotes[height] += [nodeID]
        # Broadcast our prevote to the rest of the network
        for b in broadcast:
            self.env.process(self.send(nodeID, b, 'prevote', height))
            
    # Node has received a prevote 
    def receivePrevote(self, src, nodeID, broadcast, message):
        # Extract vars from message 
        height = message
        # Get node object 
        node = self.nodes[nodeID]
        print(f"{self.env.now}: {src} -> {nodeID}: receive prevote")
        # Add prevote to local list
        addTo(node.prevotes, height, src)
        # If the prevote we received is for our current height
        if height == node.height:
            # And we haven't reached a precommit quorum for the height
            if node.awaitingPrevote:
                # Check if we have reached a quorum 
                if len(node.prevotes[height]) >= self.quorum:
                    # If we have, enter precommit step and broadcast precommit 
                    node.awaitingPrevote = False
                    node.awaitingPrecom = True
                    # Save our precommit 
                    addTo(node.precommits, height, nodeID)
                    # Broadcast message
                    for b in broadcast:
                        self.env.process(self.send(nodeID, b, 'precommit', height))
                    # Now that are in the precommit step, check if we have a precommit quorum 
                    # This won't happen in the base simulation but could be caused by more
                    # complex topologies
                    self.checkPrecomQuorum(src, node, nodeID, broadcast, height)
                    
    # Node has received a precommit  
    def receivePrecommit(self, src, nodeID, broadcast, message):
        # Extract vars from message 
        height = message
        # Get node object 
        node = self.nodes[nodeID]
        print(f"{self.env.now}: {src} -> {nodeID}: receive precommit")
        # Add precommit to local list 
        addTo(node.precommits, height, src)
        # Check if we have achieved a precommit quorum
        self.checkPrecomQuorum(src, node, nodeID, broadcast, height)
        
    # Check if node has a precommit quorum
    def checkPrecomQuorum(self, src, node, nodeID, broadcast, height):
        # If the message received is for the current height 
        if height == node.height:
            # And we are awaiting a precommit quorum 
            if node.awaitingPrecom:
                # Check if we have a quorum
                if len(node.precommits[height]) >= self.quorum:
                    # If we have, the block has been commited
                    # Prepare for the next height 
                    node.awaitingPrevote = True
                    node.awaitingPrecom = False
                    node.height += 1
                    print(f"{self.env.now}: {nodeID} : Committed {height}")
                    # If we are the next leader, propose block
                    if nodeID == self.leader[node.height]:
                        self.propose(src, node, nodeID, broadcast)
                    
    # Propose a new block 
    def propose(self, src, node, nodeID, broadcast):      
        # If the simulation allows for more blocks
        if node.height < self.MAXBLOCK:
            # Propose
            print(f"{self.env.now}: {nodeID} : Proposing {node.height}")
            for b in broadcast:
                self.env.process(self.send(nodeID, b, 'proposal', node.height))  
            # Precalculate next leader
            self.nextLeader(self, node)
            # Mark proposal time 
            self.blocktimes += [self.env.now]
                            
                    
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            