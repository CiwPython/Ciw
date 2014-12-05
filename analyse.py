"""
Script to analyse a data directory
"""
import yaml
from sys import argv

directory = argv[1]
parameter_file = directory + 'parameters.yml'
data_file = directory + 'data.yml'

print 50 * '='
print 'Reading from directory %s' % directory

parameter_file = open(parameter_file, 'r')
parameters = yaml.load(parameter_file)
print parameters['Arrival_rates']['Class 0']
parameter_file.close()
