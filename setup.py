from setuptools import setup

setup(
    name='Ciw',
    version='0.0.1dev',
    author='Geraint Palmer, Vincent Knight',
    author_email=('palmer.geraint@googlemail.com'),
    packages = ['ciw'],
    scripts = ['run_simulation'],
    description='A discrete event simulation framework for open queueing networks',
)
