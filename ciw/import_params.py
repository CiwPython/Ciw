import os
import yaml


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