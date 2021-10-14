"""setup.py"""
from setuptools import setup

setup(
    name='morp',
    version='0.0.1',
    description='Description',
    author='r1yk',
    license='MIT',
    install_requires=[
        'mido>=1.2.10',
        'python-rtmidi>=1.4.9'
    ],
    packages=['morp', 'morp.effects'],
    package_dir={'morp': 'morp', 'morp.effects': 'morp/effects'}
)
