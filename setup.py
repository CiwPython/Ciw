from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGES.rst') as changes_file:
    changes = changes_file.read()

setup(
    name='Ciw',
    version='0.2.5',
    url='https://github.com/geraintpalmer/Ciw',
    author='Geraint Palmer, Vincent Knight',
    author_email='palmer.geraint@googlemail.com',
    packages=['ciw'],
    description='A discrete event simulation library for open queueing networks',
    long_description=readme + '\n\n' + changes,
    install_requires=["PyYAML", "networkx", "hypothesis", "numpy"],
)
