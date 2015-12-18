from setuptools import setup

setup(
    name='Ciw',
    version='0.0.1',
    author='Geraint Palmer, Vincent Knight',
    author_email=('palmer.geraint@googlemail.com'),
    packages = ['ciw'],
    scripts = ['run_simulation'],
    description='A discrete event simulation framework for open queueing networks',
    install_requires=["PyYAML==3.11", "networkx==1.9.1", "docopt==0.6.2",
                      "hypothesis==1.17"]
)
