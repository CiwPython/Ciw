import networkx as nx

class NoDetection(object):
    """
    A generic class for all deadlock detector classes to inherit from.
    Using this class is equivalent to having no deadlock detection
    capabilities.
    """
    def __init__(self):
        """
        Initialises the detection mechanism class.
        """
        pass

    def initialise_at_node(self, node):
        """
        Initialises the detection mechanism when the node is created.
        """
        pass

    def detect_deadlock(self):
        """
        Returns True is deadlock is reached, False otherwise.
        """
        return False
    
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

    def action_at_detatch_server(self, server):
        """
        The action taken at the 'detatch_server' method of the node.
        """
        pass


class StateDigraph(NoDetection):
    """
    The state digraph method keeps track of a directed graph of the
    simulation state, where:
        - Vertices represent Servers
        - Edges represent blockage relationships, such that there
          is a directed edge from vertices j -> k iff the customer
          at server j is blocked from entering the node that
          contains k.
    Deadlock is equivalent to a knot in the directed graph.
    """
    def __init__(self):
        """
        Initialises the state digraph detection mechanism class.
        """
        self.statedigraph = nx.DiGraph()

    def initialise_at_node(self, node):
        """
        Initialises the state digraph when the node is created.
        Adds the servers of that node if c < Inf.
        """
        if node.c < float('Inf'):
            self.statedigraph.add_nodes_from([str(s) for s in node.servers])

    def detect_deadlock(self):
        """
        Detects whether the system is in a deadlocked state,
        that is, is there a knot. Note that this code is taken
        and adapted from the NetworkX Developer Zone Ticket
        #663 knot.py (09/06/2015).
        """
        knots = []
        for c in nx.strongly_connected_components(self.statedigraph):
            subgraph = self.statedigraph.subgraph(c)
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
        The action taken at the 'attach_server' method of the node:
          - If new customer joins server, and they're server is still
            blocking a customer, then that edge needs to remain.
            However it was removed at the action_at_detatch_server, so
            it needs to be added back in.
        """
        for blq in node.blocked_queue:
            inds = [ind for ind in node.simulation.nodes[
                blq[0]].all_individuals if ind.id_number == blq[1]]
            ind = inds[0]
            if ind != individual:
                self.statedigraph.add_edge(str(ind.server), str(server))

    def action_at_blockage(self, individual, next_node):
        """
        The action takn at the 'block_individual' method of the node:
          - Add edges between blocked server and servers of the next node.
        """
        for svr in next_node.servers:
            self.statedigraph.add_edge(str(individual.server), str(svr))

    def action_at_detatch_server(self, server):
        """
        The action taken at the 'detatch_server' method of the node:
          - Remove any edges of servers who have been detatched.
        """
        self.statedigraph.remove_edges_from(
            list(
                self.statedigraph.in_edges(str(server))
            ) + list(
                self.statedigraph.out_edges(str(server)))
            )
