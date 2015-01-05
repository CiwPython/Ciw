"""
Usage: setup_directory.py [<dir_name>]

Arguments:
	dir_name	: optional name of the directory, if ommitted current date and time is used

Options:
	-h 			: displays this help file
"""


import yaml
import shutil
from datetime import datetime
import os
import docopt


def create_data_directory(directory_name=False):
    """
    A function to create a directory:

    - A csv file with the data
    - A parameters file with the input parameters

    Tests::
        >>> from glob import glob
        >>> './logs_test' in [x[0] for x in os.walk('./')]
        False
        >>> create_data_directory('test')
        >>> './logs_test' in [x[0] for x in os.walk('./')]
        True
        >>> shutil.rmtree('./logs_test')  # Removing the test directory
        >>> './logs_test' in [x[0] for x in os.walk('./')]
        False

    """
    basename = "logs"
    if not directory_name:
        suffix = datetime.now().strftime("%y%m%d_%H%M%S")
    else:
        suffix = directory_name
    directory = "_".join([basename, suffix]) # e.g. 'mylogfile_120508_171442'
    directory_name = directory
    if not os.path.exists('./' + directory):
            os.makedirs('./' + directory)
    return directory_name



arguments = docopt.docopt(__doc__)
dirname = arguments['<dir_name>']
directory_name = create_data_directory(dirname)
shutil.move('parameters.yml', directory_name)


print 'Directory created: ' + directory_name