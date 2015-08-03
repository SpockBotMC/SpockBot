from distutils.core import setup
from setuptools import find_packages

setup (
    name='spock',
    description='Minecraft library in python',
    long_description=open('README.md').read(),
    version='1.2',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'PyCrypto >= 2.6.1',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ]
)
