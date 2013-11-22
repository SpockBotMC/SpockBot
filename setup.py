from distutils.core import setup

setup (
    name='spock',
    version='1.2',
    packages=[
    	'spock', 
    	'spock.mcp', 
    	'spock.mcmap',
    	'spock.plugins',
    	'spock.plugins.core',
    	'spock.plugins.helpers',
    ],
)
