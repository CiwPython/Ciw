import os
import yaml
import copy
import types
import ciw.dists
from .network import *

def get_distribution(dist):
    """
    For use when parameters are read in from a .yml file.
    Returns instances of the distribution classes that
    correspond to the indicator string in the .yml file.
    """
    if dist[0] == 'Uniform':
       return ciw.dists.Uniform(dist[1], dist[2])
    if dist[0] == 'Deterministic':
        return ciw.dists.Deterministic(dist[1])
    if dist[0] == 'Triangular':
        return ciw.dists.Triangular(dist[1], dist[2], dist[3])
    if dist[0] == 'Exponential':
        return ciw.dists.Exponential(dist[1])
    if dist[0] == 'Gamma':
        return ciw.dists.Gamma(dist[1], dist[2])
    if dist[0] == 'Normal':
        return ciw.dists.Normal(dist[1], dist[2])
    if dist[0] == 'Lognormal':
        return ciw.dists.Lognormal(dist[1], dist[2])
    if dist[0] == 'Weibull':
        return ciw.dists.Weibull(dist[1], dist[2])
    if dist[0] == 'Pmf':
        return ciw.dists.Pmf(dist[1], dist[2])
    if dist[0] == 'NoArrivals':
        return ciw.dists.NoArrivals()
    return ciw.dists.Distribution()

def create_network(arrival_distributions=None,
                   baulking_functions=None,
                   class_change_matrices=None,
                   number_of_servers=None,
                   priority_classes=None,
                   queue_capacities=None,
                   service_distributions=None,
                   routing=None,
                   batching_distributions=None):
    """
    Takes in kwargs, creates dictionary.
    """
    if arrival_distributions == None or number_of_servers == None or service_distributions == None:
        raise ValueError('arrival_distributions, service_distributions and number_of_servers are required arguments.')

    params = {
        'arrival_distributions': arrival_distributions,
        'number_of_servers': number_of_servers,
        'service_distributions': service_distributions
    }

    if baulking_functions != None:
        params['baulking_functions'] = baulking_functions
    if class_change_matrices != None:
        params['class_change_matrices'] = class_change_matrices
    if priority_classes != None:
        params['priority_classes'] = priority_classes
    if queue_capacities != None:
        params['queue_capacities'] = queue_capacities
    if routing != None:
        params['routing'] = routing
    if batching_distributions != None:
        params['batching_distributions'] = batching_distributions

    return create_network_from_dictionary(params)


def load_parameters(directory_name):
    """
    Loads the .yml file parameters to a dictionary.
    """
    root = os.getcwd()
    directory = os.path.join(root, directory_name)
    parameter_file_name = directory
    parameter_file = open(parameter_file_name, 'r')
    parameters = yaml.load(parameter_file, Loader=yaml.FullLoader)
    parameter_file.close()
    return parameters


def create_network_from_yml(directory_name):
    """
    Creates a Network object form a yaml file.
    """
    params_input = load_parameters(directory_name)
    params = fill_out_dictionary(params_input)
    for clss in params['arrival_distributions']:
        dists = []
        for dist in params['arrival_distributions'][clss]:
            dists.append(get_distribution(dist))
        params['arrival_distributions'][clss] = dists
    for clss in params['service_distributions']:
        dists = []
        for dist in params['service_distributions'][clss]:
            dists.append(get_distribution(dist))
        params['service_distributions'][clss] = dists
    validify_dictionary(params)
    return create_network_from_dictionary(params)


def create_network_from_dictionary(params_input):
    """
    Creates a Network object from a parameters dictionary.
    """
    params = fill_out_dictionary(params_input)
    validify_dictionary(params)
    # Then make the Network object
    arrivals = [params['arrival_distributions']['Class ' + str(clss)]
        for clss in range(len(params['arrival_distributions']))]
    services = [params['service_distributions']['Class ' + str(clss)]
        for clss in range(len(params['service_distributions']))]
    if all(isinstance(f, types.FunctionType) for f in params['routing']):
        routing = params['routing']
    else:
        routing = [params['routing']['Class ' + str(clss)]
            for clss in range(len(params['routing']))]
    priorities = [params['priority_classes']['Class ' + str(clss)]
        for clss in range(len(params['priority_classes']))]
    baulking_functions = [params['baulking_functions']['Class ' + str(clss)]
        for clss in range(len(params['baulking_functions']))]
    batches = [params['batching_distributions']['Class ' + str(clss)]
        for clss in range(len(params['batching_distributions']))]
    number_of_classes = params['number_of_classes']
    number_of_nodes = params['number_of_nodes']
    queueing_capacities = [float(i) if i == "Inf" else i for i in params['queue_capacities']]
    class_change_matrices = params.get('class_change_matrices',
        {'Node ' + str(nd + 1): None for nd in range(number_of_nodes)})
    number_of_servers, schedules, nodes, classes, preempts = [], [], [], [], []
    for c in params['number_of_servers']:
        if isinstance(c, (tuple, list)):
            if isinstance(c, tuple):
                s = c[0]
                p = c[1]
            if isinstance(c, list):
                s = c
                p = False
            number_of_servers.append('schedule')
            schedules.append(s)
            preempts.append(p)
        elif c == 'Inf':
            number_of_servers.append(float(c))
            schedules.append(None)  
            preempts.append(False)
        else:
            number_of_servers.append(c)
            schedules.append(None) 
            preempts.append(False)   
    for nd in range(number_of_nodes):
        nodes.append(ServiceCentre(
            number_of_servers[nd],
            queueing_capacities[nd],
            class_change_matrices['Node ' + str(nd + 1)],
            schedules[nd],
            preempts[nd]))
    for clss in range(number_of_classes):
        if all(isinstance(f, types.FunctionType) for f in params['routing']):
            classes.append(CustomerClass(
                arrivals[clss],
                services[clss],
                routing,
                priorities[clss],
                baulking_functions[clss],
                batches[clss]))
        else:
            classes.append(CustomerClass(
                arrivals[clss],
                services[clss],
                routing[clss],
                priorities[clss],
                baulking_functions[clss],
                batches[clss]))
    n = Network(nodes, classes)
    if all(isinstance(f, types.FunctionType) for f in params['routing']):
        n.process_based = True
    else:
        n.process_based = False
    return n


def fill_out_dictionary(params_input):
    """
    Fills out the parameters dictionary with the
    default values of the optional arguments.
    """
    params = copy.deepcopy(params_input)
    if isinstance(params['arrival_distributions'], list):
        arr_dists = params['arrival_distributions']
        params['arrival_distributions'] = {'Class 0': arr_dists}
    if isinstance(params['service_distributions'], list):
        srv_dists = params['service_distributions']
        params['service_distributions'] = {'Class 0': srv_dists}
    if 'routing' in params:            
        if all(isinstance(f, list) for f in params['routing']):
            rtng_mat = params['routing']
            params['routing'] = {'Class 0': rtng_mat}
    if 'baulking_functions' in params:
        if isinstance(params['baulking_functions'], list):
            blk_fncs = params['baulking_functions']
            params['baulking_functions'] = {'Class 0': blk_fncs}
    if 'batching_distributions' in params:
        if isinstance(params['batching_distributions'], list):
            btch_dists = params['batching_distributions']
            params['batching_distributions'] = {'Class 0': btch_dists}

    default_dict = {
        'name': 'Simulation',
        'routing': {'Class ' + str(i): [[0.0]]
            for i in range(len(params['arrival_distributions']))},
        'number_of_nodes': len(params['number_of_servers']),
        'number_of_classes': len(params['arrival_distributions']),
        'queue_capacities': [float('inf') for _ in range(len(
            params['number_of_servers']))],
        'priority_classes': {'Class ' + str(i): 0
            for i in range(len(params['arrival_distributions']))},
        'baulking_functions': {'Class ' + str(i): [
            None for _ in range(len(params['number_of_servers']))]
            for i in range(len(params['arrival_distributions']))},
        'batching_distributions': {'Class ' + str(i): [
            ciw.dists.Deterministic(1) for _ in range(
            len(params['number_of_servers']))] for i in range(
            len(params['arrival_distributions']))}
        }

    for a in default_dict:
        params[a] = params.get(a, default_dict[a])
    return params


def validify_dictionary(params):
    """
    Raises errors if there is something wrong with the
    parameters dictionary.
    """
    if all(isinstance(f, types.FunctionType) for f in params['routing']):
        consistant_num_classes = (
            params['number_of_classes'] ==
            len(params['arrival_distributions']) ==
            len(params['service_distributions']) ==
            len(params['batching_distributions']))
    else:
        consistant_num_classes = (
            params['number_of_classes'] ==
            len(params['arrival_distributions']) ==
            len(params['service_distributions']) ==
            len(params['routing']) ==
            len(params['batching_distributions']))
    if not consistant_num_classes:
        raise ValueError('Ensure consistant number of classes is used throughout.')
    if all(isinstance(f, types.FunctionType) for f in params['routing']):
        consistant_class_names = (
            set(params['arrival_distributions']) ==
            set(params['service_distributions']) ==
            set(params['batching_distributions']) ==
            set(['Class ' + str(i) for i in range(params['number_of_classes'])]))
    else:
        consistant_class_names = (
            set(params['arrival_distributions']) ==
            set(params['service_distributions']) ==
            set(params['routing']) ==
            set(params['batching_distributions']) ==
            set(['Class ' + str(i) for i in range(params['number_of_classes'])]))
    if not consistant_class_names:
        raise ValueError('Ensure correct names for customer classes.')
    if all(isinstance(f, types.FunctionType) for f in params['routing']):
        num_nodes_count = [
        params['number_of_nodes']] + [
        len(obs) for obs in params['arrival_distributions'].values()] + [
        len(obs) for obs in params['service_distributions'].values()] + [
        len(obs) for obs in params['batching_distributions'].values()] + [
        len(params['routing'])] + [
        len(params['number_of_servers'])] + [
        len(params['queue_capacities'])]
    else:
        num_nodes_count = [
            params['number_of_nodes']] + [
            len(obs) for obs in params['arrival_distributions'].values()] + [
            len(obs) for obs in params['service_distributions'].values()] + [
            len(obs) for obs in params['routing'].values()] + [
            len(obs) for obs in params['batching_distributions'].values()] + [
            len(row) for row in [obs for obs in params['routing'].values()][0]] + [
            len(params['number_of_servers'])] + [
            len(params['queue_capacities'])]
    if len(set(num_nodes_count)) != 1:
        raise ValueError('Ensure consistant number of nodes is used throughout.')
    if not all(isinstance(f, types.FunctionType) for f in params['routing']):    
        for clss in params['routing'].values():
            for row in clss:
                if sum(row) > 1.0 or min(row) < 0.0 or max(row) > 1.0:
                    raise ValueError('Ensure that routing matrix is valid.')
    neg_numservers = any([(isinstance(obs, int) and obs < 0) for obs in params['number_of_servers']])
    valid_capacities = all([((isinstance(obs, int) and obs >= 0) or obs==float('inf') or obs=='Inf') for obs in params['queue_capacities']])
    if neg_numservers:
        raise ValueError('Number of servers must be positive integers.')
    if not valid_capacities:
        raise ValueError('Queue capacities must be positive integers or zero.')
    if 'class_change_matrices' in params:
        num_nodes = len(params['class_change_matrices']) == params['number_of_nodes']
        node_names = set(params['class_change_matrices']) == set(['Node ' + str(i+1) for i in range(params['number_of_nodes'])])
        if not (num_nodes and node_names):
            raise ValueError('Ensure correct nodes used in class_change_matrices.')
        for nd in params['class_change_matrices'].values():
            for row in nd:
                if sum(row) > 1.0 or min(row) < 0.0 or max(row) > 1.0:
                    raise ValueError('Ensure that class change matrix is valid.')
    for n in params['number_of_servers']:
        if isinstance(n, str) and n != 'Inf':
            if n not in params:
                raise ValueError('No schedule ' + str(n) + ' defined.')
