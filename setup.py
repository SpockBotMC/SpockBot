from distutils.core import setup

setup (
    name='spock',
    version='1.1',
    packages=[
    	'spock', 
    	'spock.mcp', 
    	'spock.net', 
    	'spock.net.clients',
    	'spock.net.plugins',
    	'spock.net.plugins.core',
    	'spock.net.plugins.helpers',
    ],
)