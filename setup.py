from setuptools import setup

setup(
    name='Ciw',
    version='0.2.2',
    author='Geraint Palmer, Vincent Knight',
    author_email=('palmer.geraint@googlemail.com'),
    packages = ['ciw'],
    description='A discrete event simulation framework for open queueing networks',
    install_requires=["PyYAML", "networkx", "hypothesis", "numpy"]
)
