import networkx as nx


class NoDeadlockDetection(object):
    """
    A generic class to detect deadlock in queueing networks.
    This overall class is equivalent to having no deadlock
    detection capabilities.
    """
    def __init__(self):
        """
        Initialises the detection mechanism class
        """
        pass

    def initialise_at_node(self, node):
        """
        Initialises the detection mechanism when the node is created
        """
        pass
    
    def action_at_attach_server(self, node, server, individual):
        """
        The action taken at the 'attach_server' method of the node.
        """
        pass

    def action_at_blockage(self, individual, next_node):
        """
        The action takn at the 'block_individual' method of the node.
        """
        pass

    def action_at_detach_server(self, server):
        """
        The action taken at the 'detatch_server' method of the node.
        """
        pass


class StateDigraphMethod(NoDeadlockDetection):
    """
    The state digraph method uses:
        Vertices -- Servers
        Edges -- Blockage relationship such that there is a
        directed edge from vertices j -> k iff the customer
        at server j is blocked from entering the node that
        contains k.
    """
    def __init__(self):
        """
        Initialises the state digraph detection mechanism class
        """
        self.statedigraph = nx.DiGraph()

    def initialise_at_node(self, node):
        """
        Initialises the state digraph when the node is created.
        Adds the servers of that node if c < Inf.
        """
        if node.c < float('Inf'):
            self.statedigraph.add_nodes_from([str(s)for s in node.servers])

    def detect_deadlock(self):
        """
        Detects whether the system is in a deadlocked state,
        that is, is there a knot. Note that this code is taken
        and adapted from the NetworkX Developer Zone Ticket
        #663 knot.py (09/06/2015)
        """
        knots = []
        for subgraph in nx.strongly_connected_component_subgraphs(self.statedigraph):
            nodes = set(subgraph.nodes())
            if len(nodes) == 1:
                n = nodes.pop()
                nodes.add(n)
                if set(self.statedigraph.successors(n)) == nodes:
                    knots.append(subgraph)
            else:
                for n in nodes:
                    successors = nx.descendants(self.statedigraph, n)
                    if successors <= nodes:
                        knots.append(subgraph)
                        break
        if len(knots) > 0:
            return True
        return False

    def action_at_attach_server(self, node, server, individual):
        """
        The action taken at the 'attach_server' method of the node.
        """
        for blq in node.blocked_queue:
            inds = [ind for ind in node.simulation.nodes[
                blq[0]].all_individuals if ind.id_number == blq[1]]
            ind = inds[0]
            if ind != individual:
                self.statedigraph.add_edge(
                    str(ind.server), str(server))

    def action_at_blockage(self, individual, next_node):
        """
        The action takn at the 'block_individual' method of the node.
        """
        for svr in next_node.servers:
            self.statedigraph.add_edge(
                str(individual.server), str(svr))

    def action_at_detach_server(self, server):
        """
        The action taken at the 'detatch_server' method of the node.
        """
        self.statedigraph.remove_edges_from(
            self.statedigraph.in_edges(
            str(server)) + self.statedigraph.out_edges(
            str(server)))
