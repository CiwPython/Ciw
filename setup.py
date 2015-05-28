from distutils.core import setup

setup(
    name='Open Queueing Network Simulation',
    version='0.0.1',
    author='Geraint Palmer, Vince Knight',
    author_email=('palmer.geraint@googlemail.com'),
    scripts=['simulation.py, analyse.py, setup_directory.py'],
    description='A discrete event simulation framework for open queueing networks',
    install_requires=[
        "matplotlib >= 1.4.2",
        "PyYAML==3.11",
        "networkx==1.9.1",
        "numpy==1.9.2",
        "scipy==0.15.1",
    ],
)
