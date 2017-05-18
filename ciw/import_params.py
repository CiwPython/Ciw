import os
import yaml
import copy
from .network import *


def create_network(Arrival_distributions=None,
                   Baulking_functions=None,
                   Class_change_matrices=None,
                   Number_of_servers=None,
                   Priority_classes=None,
                   Queue_capacities=None,
                   Service_distributions=None,
                   Transition_matrices=None):
    """
    Takes in kwargs, creates dictionary.
    """
    if Arrival_distributions == None or Number_of_servers == None or Service_distributions == None:
        raise ValueError('Arrival_distributions, Service_distributions and Number_of_servers are required arguments.')

    params = {
        'Arrival_distributions': Arrival_distributions,
        'Number_of_servers': Number_of_servers,
        'Service_distributions': Service_distributions
    }

    if Baulking_functions != None:
        params['Baulking_functions'] = Baulking_functions
    if Class_change_matrices != None:
        params['Class_change_matrices'] = Class_change_matrices
    if Priority_classes != None:
        params['Priority_classes'] = Priority_classes
    if Queue_capacities != None:
        params['Queue_capacities'] = Queue_capacities
    if Transition_matrices != None:
        params['Transition_matrices'] = Transition_matrices

    return create_network_from_dictionary(params)


def load_parameters(directory_name):
    """
    Loads the parameters into the model
    """
    root = os.getcwd()
    directory = os.path.join(root, directory_name)
    parameter_file_name = directory
    parameter_file = open(parameter_file_name, 'r')
    parameters = yaml.load(parameter_file)
    parameter_file.close()
    return parameters


def create_network_from_yml(directory_name):
    """
    Creates a Network object form a yaml file
    """
    params_input = load_parameters(directory_name)
    params = fill_out_dictionary(params_input)
    validify_dictionary(params)
    return create_network_from_dictionary(params)


def create_network_from_dictionary(params_input):
    """
    Creates a Network object from a parameters dictionary
    """
    params = fill_out_dictionary(params_input)
    validify_dictionary(params)
    # Then make the Network object
    arrivals = [params['Arrival_distributions']['Class ' + str(clss)]
        for clss in range(len(params['Arrival_distributions']))]
    services = [params['Service_distributions']['Class ' + str(clss)]
        for clss in range(len(params['Service_distributions']))]
    transitions = [params['Transition_matrices']['Class ' + str(clss)]
        for clss in range(len(params['Transition_matrices']))]
    priorities = [params['Priority_classes']['Class ' + str(clss)]
        for clss in range(len(params['Priority_classes']))]
    baulking_functions = [params['Baulking_functions']['Class ' + str(clss)]
        for clss in range(len(params['Baulking_functions']))]
    number_of_classes = params['Number_of_classes']
    number_of_nodes = params['Number_of_nodes']
    queueing_capacities = [float(i) if i == "Inf" else i for i in params['Queue_capacities']]
    class_change_matrices = params.get('Class_change_matrices',
        {'Node ' + str(nd + 1): None for nd in range(number_of_nodes)})
    number_of_servers, schedules, nodes, classes, preempts = [], [], [], [], []
    for c in params['Number_of_servers']:
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
        classes.append(CustomerClass(
            arrivals[clss],
            services[clss],
            transitions[clss],
            priorities[clss],
            baulking_functions[clss]))
    return Network(nodes, classes)


def fill_out_dictionary(params_input):
    """
    Fills out the parameters dictionary with the
    optional arguments
    """
    params = copy.deepcopy(params_input)
    if isinstance(params['Arrival_distributions'], list):
        arr_dists = params['Arrival_distributions']
        params['Arrival_distributions'] = {'Class 0': arr_dists}
    if isinstance(params['Service_distributions'], list):
        srv_dists = params['Service_distributions']
        params['Service_distributions'] = {'Class 0': srv_dists}
    if 'Transition_matrices' in params:
        if isinstance(params['Transition_matrices'], list):
            trns_mat = params['Transition_matrices']
            params['Transition_matrices'] = {'Class 0': trns_mat}
    if 'Baulking_functions' in params:
        if isinstance(params['Baulking_functions'], list):
            blk_fncs = params['Baulking_functions']
            params['Baulking_functions'] = {'Class 0': blk_fncs}

    default_dict = {
        'Name': 'Simulation',
        'Transition_matrices': {'Class ' + str(i): [[0.0]]
            for i in range(len(params['Arrival_distributions']))},
        'Number_of_nodes': len(params['Number_of_servers']),
        'Number_of_classes': len(params['Arrival_distributions']),
        'Queue_capacities': ['Inf' for _ in range(len(
            params['Number_of_servers']))],
        'Priority_classes': {'Class ' + str(i): 0
            for i in range(len(params['Arrival_distributions']))},
        'Baulking_functions': {'Class ' + str(i): [
            None for _ in range(len(params['Number_of_servers']))]
            for i in range(len(params['Arrival_distributions']))}
        }

    for a in default_dict:
        params[a] = params.get(a, default_dict[a])
    return params


def validify_dictionary(params):
    """
    Raises errors if there is something wrong with the
    parameters dictionary
    """
    consistant_num_classes = (
        params['Number_of_classes'] ==
        len(params['Arrival_distributions']) ==
        len(params['Service_distributions']) ==
        len(params['Transition_matrices']))
    if not consistant_num_classes:
        raise ValueError('Ensure consistant number of classes is used throughout.')
    consistant_class_names = (
        set(params['Arrival_distributions']) ==
        set(params['Service_distributions']) ==
        set(params['Transition_matrices']) ==
        set(['Class ' + str(i) for i in range(params['Number_of_classes'])]))
    if not consistant_class_names:
        raise ValueError('Ensure correct names for customer classes.')
    num_nodes_count = [
        params['Number_of_nodes']] + [
        len(obs) for obs in list(params['Arrival_distributions'].values())] + [
        len(obs) for obs in list(params['Service_distributions'].values())] + [
        len(obs) for obs in list(params['Transition_matrices'].values())] + [
        len(row) for row in [obs for obs in list(params['Transition_matrices'].values())][0]] + [
        len(params['Number_of_servers'])] + [
        len(params['Queue_capacities'])]
    if len(set(num_nodes_count)) != 1:
        raise ValueError('Ensure consistant number of nodes is used throughout.')
    for clss in list(params['Transition_matrices'].values()):
        for row in clss:
            if sum(row) > 1.0 or min(row) < 0.0 or max(row) > 1.0:
                raise ValueError('Ensure that transition matrix is valid.')
    dists = [params['Service_distributions']['Class ' + str(i)][j][0] for i in range(params['Number_of_classes']) for j in range(params['Number_of_nodes'])] + [
        params['Arrival_distributions']['Class ' + str(i)][j][0] for i in range(params['Number_of_classes']) for j in range(params['Number_of_nodes']) if params['Arrival_distributions']['Class ' + str(i)][j] != 'NoArrivals']
    if not set(dists).issubset(set([
        'Uniform', 'Triangular', 'Deterministic',
        'Exponential', 'Gamma', 'Lognormal',
        'Weibull', 'Empirical', 'Custom', 'UserDefined',
        'TimeDependent', 'Normal', 'Sequential'])):
        raise ValueError('Ensure that valid Arrival and Service Distributions are used.')
    neg_numservers = any([(isinstance(obs, int) and obs < 0) for obs in params['Number_of_servers']])
    valid_capacities = all([((isinstance(obs, int) and obs >= 0) or obs=='Inf') for obs in params['Queue_capacities']])
    if neg_numservers:
        raise ValueError('Number of servers must be positive integers.')
    if not valid_capacities:
        raise ValueError('Queue capacities must be positive integers or zero.')
    if 'Class_change_matrices' in params:
        num_nodes = len(params['Class_change_matrices']) == params['Number_of_nodes']
        node_names = set(params['Class_change_matrices']) == set(['Node ' + str(i+1) for i in range(params['Number_of_nodes'])])
        if not (num_nodes and node_names):
            raise ValueError('Ensure correct nodes used in Class_change_matrices.')
        for nd in list(params['Class_change_matrices'].values()):
            for row in nd:
                if sum(row) > 1.0 or min(row) < 0.0 or max(row) > 1.0:
                    raise ValueError('Ensure that class change matrix is valid.')
    for n in params['Number_of_servers']:
        if isinstance(n, str) and n != 'Inf':
            if n not in params:
                raise ValueError('No schedule ' + str(n) + ' defined.')

    # Distribution parameters:::
    for clss in list(params['Arrival_distributions'].values()):
        for nd in clss:
            if nd != 'NoArrivals':
                if nd[0] == 'Uniform':
                    if nd[1] < 0.0 or nd[2] < 0.0:
                        raise ValueError('Uniform distribution must sample positive numbers only.')
                    if nd[2] <= nd[1]:
                        raise ValueError('Upper limit of Uniform distribution must be greater than the lower limit.')
                if nd[0] == 'Deterministic':
                    if nd[1] < 0.0:
                        raise ValueError('Deterministic distribution must sample positive numbers only.')
                if nd[0] == 'Triangular':
                    if nd[1] < 0.0 or nd[2] < 0.0 or nd[3] < 0.0:
                        raise ValueError('Triangular distribution must sample positive numbers only.')
                    if nd[1] > nd[2] or nd[1] >= nd[3] or nd[3] >= nd[2]:
                        raise ValueError('Triangular distribution\'s median must lie between the lower and upper limits.')
                if nd[0] == 'Custom':
                        V, P = nd[1], nd[2]
                        for el in P:
                            if not isinstance(el, float) or el < 0.0:
                                raise ValueError('Probabilities for Custom distribution need to be floats between 0.0 and 1.0.')
                        for el in V:
                            if el < 0.0:
                                raise ValueError('Custom distribution must sample positive values only.')
                if nd[0] == 'Empirical':
                    if isinstance(nd[1], list):
                        if any([el<0.0 for el in nd[1]]):
                            raise ValueError('Empirical distribution must sample positive floats.')
    for clss in list(params['Service_distributions'].values()):
        for nd in clss:
            if nd[0] == 'Uniform':
                if nd[1] < 0.0 or nd[2] < 0.0:
                    raise ValueError('Uniform distribution must sample positive numbers only.')
                if nd[2] <= nd[1]:
                    raise ValueError('Upper limit of Uniform distribution must be greater than the lower limit.')
            if nd[0] == 'Deterministic':
                if nd[1] < 0.0:
                    raise ValueError('Deterministic distribution must sample positive numbers only.')
            if nd[0] == 'Triangular':
                if nd[1] < 0.0 or nd[2] < 0.0 or nd[3] < 0.0:
                    raise ValueError('Triangular distribution must sample positive numbers only.')
                if nd[1] > nd[2] or nd[1] >= nd[3] or nd[3] >= nd[2]:
                    raise ValueError('Triangular distribution\'s median must lie between the lower and upper limits.')
            if nd[0] == 'Custom':
                    V, P = nd[1], nd[2]
                    for el in P:
                        if not isinstance(el, float) or el < 0.0:
                            raise ValueError('Probabilities for Custom distribution need to be floats between 0.0 and 1.0.')
                    for el in V:
                        if el < 0.0:
                            raise ValueError('Custom distribution must sample positive values only.')
            if nd[0] == 'Empirical' or nd[0] == 'Sequential':
                if isinstance(nd[1], list):
                    if any([el<0.0 for el in nd[1]]):
                        raise ValueError('Empirical distribution must sample positive floats.')

