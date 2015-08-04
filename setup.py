from distutils.core import setup

from setuptools import find_packages

setup(
    name='spock',
    description='A pure python framework that implements the 1.8 Minecraft '
                'protocol for building Minecraft clients',
    license='MIT',
    long_description=open('README.rst').read(),
    version='0.1.2',
    url='https://github.com/SpockBotMC/SpockBot',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'PyCrypto >= 2.6.1',
    ],
    keywords=['minecraft'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ]
)
