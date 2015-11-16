import os
import yaml


def load_parameters(directory_name):
    """
    Loads the parameters into the model

        >>> P = load_parameters('tests/datafortesting/logs_test_for_simulation/')
        >>> P
        {'Arrival_rates': {'Class 2': [2.0, 1.0, 2.0, 0.5], 'Class 1': [2.0, 3.0, 6.0, 4.0], 'Class 0': [3.0, 7.0, 4.0, 1.0]}, 'Number_of_nodes': 4, 'detect_deadlock': False, 'Simulation_time': 2500, 'Number_of_servers': [9, 10, 8, 8], 'Queue_capacities': [20, 'Inf', 30, 'Inf'], 'Number_of_classes': 3, 'Service_rates': {'Class 2': [['Deterministic', 0.3], ['Deterministic', 0.2], ['Exponential', 8.0], ['Exponential', 9.0]], 'Class 1': [['Exponential', 7.0], ['Triangular', 0.1, 0.8, 0.85], ['Exponential', 8.0], ['Exponential', 5.0]], 'Class 0': [['Exponential', 7.0], ['Exponential', 7.0], ['Gamma', 0.4, 0.6], ['Deterministic', 0.5]]}, 'Transition_matrices': {'Class 2': [[0.0, 0.0, 0.4, 0.3], [0.1, 0.1, 0.1, 0.1], [0.1, 0.3, 0.2, 0.2], [0.0, 0.0, 0.0, 0.3]], 'Class 1': [[0.6, 0.0, 0.0, 0.2], [0.1, 0.1, 0.2, 0.2], [0.9, 0.0, 0.0, 0.0], [0.2, 0.1, 0.1, 0.1]], 'Class 0': [[0.1, 0.2, 0.1, 0.4], [0.2, 0.2, 0.0, 0.1], [0.0, 0.8, 0.1, 0.1], [0.4, 0.1, 0.1, 0.0]]}}
    """
    root = os.getcwd()
    directory = os.path.join(root, directory_name)
    parameter_file_name = directory + 'parameters.yml'
    parameter_file = open(parameter_file_name, 'r')
    parameters = yaml.load(parameter_file)
    parameter_file.close()

    if parameters['Number_of_nodes'] == 1:
        for cls in parameters['Transition_matrices']:
            parameters['Transition_matrices'][cls] = [parameters['Transition_matrices'][cls]]

    return parameters