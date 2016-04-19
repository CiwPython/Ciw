import os
import yaml
from network import *


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

def Network_From_Dictionary(params):
    """
    Creates a Network object from a parameters dictionary
    """
    if isinstance(params['Arrival_distributions'], dict):
        arrivals = [params['Arrival_distributions']['Class ' + str(cls)]
            for cls in xrange(len(params['Arrival_distributions']))]
    if isinstance(params['Arrival_distributions'], list):
        arrivals = [params['Arrival_distributions']]
    if isinstance(params['Service_distributions'], dict):
        services = [params['Service_distributions']['Class ' + str(cls)]
            for cls in xrange(len(params['Service_distributions']))]
    if isinstance(params['Service_distributions'], list):
        services = [params['Service_distributions']]
    if isinstance(params['Transition_matrices'], dict):
        transitions = [params['Transition_matrices']['Class ' + str(cls)]
            for cls in xrange(len(params['Transition_matrices']))]
    if isinstance(params['Transition_matrices'], list):
        transitions = [params['Transition_matrices']]
    number_of_classes = params.get('Number_of_classes', len(arrivals))
    number_of_nodes = params.get('Number_of_nodes', len(arrivals[0]))
    queueing_capacities = params.get('Queue_capacities',
        ['Inf' for i in xrange(number_of_nodes)])
    class_change_matrices = params.get('Class_change_matrices',
        {'Node ' + str(nd + 1): None for nd in xrange(number_of_nodes)})
    number_of_servers, schedules, nodes, classes = [], [], [], []
    for c in params['Number_of_servers']:
        if isinstance(c, str) and c != 'Inf':
            number_of_servers.append('schedule')
            schedules.append(params[c])
        else:
            number_of_servers.append(c)
            schedules.append(None)    
    for nd in xrange(number_of_nodes):
        nodes.append(ServiceCentre(
            number_of_servers[nd],
            queueing_capacities[nd],
            class_change_matrices['Node ' + str(nd + 1)],
            schedules[nd]))
    for cls in xrange(number_of_classes):
        classes.append(CustomerClass(
            arrivals[cls],
            services[cls],
            transitions[cls]))
    return Network(nodes, classes)

def Network_From_File(directory_name):
    """
    Creates a Network object form a yaml file
    """
    params = load_parameters(directory_name)
    return Network_From_Dictionary(params)