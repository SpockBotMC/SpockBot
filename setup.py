from distutils.core import setup

from setuptools import find_packages

VERSION = '0.1.3'

setup(
    name='spockbot',
    description='High level Python framework for building Minecraft '
                'clients and bots',
    license='MIT',
    long_description=open('README.rst').read(),
    version=VERSION,
    url='https://github.com/SpockBotMC/SpockBot',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'cryptography >= 0.9',
        'minecraft_data == 0.4.0',
        'six',
    ],
    keywords=['minecraft'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ]
)
