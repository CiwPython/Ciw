from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGES.rst') as changes_file:
    changes = changes_file.read()

with open('AUTHORS.rst') as authors_file:
    authors = authors_file.read()

with open('requirements.txt') as f:
    requirements = []
    for library in f.read().splitlines():
        if "hypothesis" not in library:  # Skip: used only for dev
            requirements.append(library)


# Read in the version number
exec(open('ciw/version.py', 'r').read())

setup(
    name='Ciw',
    version=__version__,
    url='https://github.com/CiwPython/Ciw',
    author='Geraint Palmer, Vincent Knight',
    author_email='palmer.geraint@googlemail.com',
    packages=find_packages(),
    description='A discrete event simulation library for open queueing networks',
    long_description=readme + '\n\n' + changes + '\n\n' + authors,
    install_requires=requirements
)
