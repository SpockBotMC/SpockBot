"""
Basic example of how to use Spock

Instructions:
- Enter the e-mail for your Minecraft account in the USERNAME field below
  and enter your password in the PASSWORD field.

- Update the SERVER to the appropriate value for your Minecraft server.

- See the example plugin that is loaded in example_plugin.py and update it
  according to your desired functionality.
"""

__author__ = 'Cosmo Harrigan'

# Set the following values:
USERNAME = ''
PASSWORD = ''
SERVER = 'localhost'

from spock import Client
from spock.plugins import DefaultPlugins

# Import the plugins you have created
from example_plugin import ExamplePlugin

# Enter your credentials and the server information
settings = {
    'start': {
        'username': USERNAME,
        'password': PASSWORD,
    },
}

# Load the plugins. Any functionality that you want to implement must be called
# from a plugin. You can define new plugins that listen for arbitrary events from
# the game. Furthermore, events can even be periodic timers that trigger a method.
plugins = DefaultPlugins
plugins.append(('example', ExamplePlugin))

# Instantiate and start the client, which will then run and wait for events to occur
client = Client(plugins=plugins, settings=settings)
client.start(SERVER, 25565)
