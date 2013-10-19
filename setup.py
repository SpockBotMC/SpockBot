from distutils.core import setup

setup (
    name='spock',
    version='1.0',
    packages=[
    	'spock', 
    	'spock.mcp', 
    	'spock.net', 
    	'spock.net.clients',
    	'spock.net.plugins',
    ],
)