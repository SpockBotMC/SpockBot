SpockBot
========

|Build Status| |Docs Status| |Coverage Status|

SpockBot currently supports Minecraft 1.8.8

Minecraft bot framework written in Python, currently under heavy development.

- Protocol stuff lives in `spock/mcp <spock/mcp>`__
- Map stuff lives in `spock/mcmap <spock/mcmap>`__
- Data stuff lives in `spock/mcdata <spock/mcdata>`__
- Core client stuff lives in `spock/plugins/core <spock/plugins/core>`__
- Helpful client stuff lives in `spock/plugins/helpers <spock/plugins/helpers>`__

Client could loosely be called "event-driven", by default plugins
register handler functions to handle events that may or may not be
emitted by other plugins. Everything is a plugin in SpockBot, including
the event loop/framework itself, so you can feel free to rip out the
entire back end and replace it with your framework or paradigm of choice.
As long as you provide the same simple APIs, other plugins won't know the
difference.

Absolutely none of this is documented so if you're uncomfortable reading
source code this might not be the framework for you. Or, better yet, hop
on IRC and help us write some docs!

Spock officially supports Python 3.x and Python 2.7.x on \*nix operating
systems and requires cryptography_. It also runs on Windows and under
PyPy 2.6.x but that's not regularly tested and might break at any given
moment. If you support one of those use cases and SpockBot breaks for you,
submit an issue with a stack trace and we'll try to fix it.


Features
--------

- World Interaction (finding, placing, breaking)
- Vanilla Physics
- Inventory (player, chests, etc)
- Crafting
- Entities


Roadmap
-------

- Pathfinding
- Vehicle Physics


Dependencies
------------

- Python 3.x or Python 2.7.x or PyPy 2.6.x
- cryptography_ 0.9+
- minecraft_data_
- six

Note
""""
cryptography library has some extra dependencies to install, you can find detailed instructions `here <https://cryptography.io/en/latest/installation/>`__.


Installation
------------

``python3 setup.py install``

Examples
--------

Refer to the `example bot <examples/basic>`__ for instructions on how to
write a bot and a plugin that provides some common functionality.

Also see `Extra examples <https://github.com/SpockBotMC/SpockBot-Extra/tree/master/examples>`__
for additional examples.

Documentation
-------------

Current docs live here https://spockbot.readthedocs.org

Support
-------

| ``#spockbot`` on Freenode
| gamingrobot or nickelpro in ``#mcdevs`` on Freenode

Contributing
------------

Instructions for contributing to SpockBot can be found in `CONTRIBUTING <CONTRIBUTING.rst>`__

Credits
-------

Inspired by `remyroy's
COPS <http://www.reddit.com/r/Civcraft/comments/13kwjm/introducing_the_cops_civcraft_online_player_status/>`__,
a Minecraft client in Python.

COPS was a service that tracked players on a minecraft server called Civcraft. It looked like `this <http://i.imgur.com/SR2qII5.jpg>`__

Protocol implementation based on `barneymc <https://github.com/barneygale/barneymc>`__.

Legal
-----

License is MIT and can be found in `LICENSE <LICENSE>`__

The NBT parser and the original protocol implementation came from other projects, relevant legal information and attribution can be found in `LEGAL <LEGAL.md>`__

.. |Build Status| image:: https://travis-ci.org/SpockBotMC/SpockBot.svg
   :target: https://travis-ci.org/SpockBotMC/SpockBot
.. |Coverage Status| image:: https://coveralls.io/repos/SpockBotMC/SpockBot/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/SpockBotMC/SpockBot?branch=master
.. |Docs Status| image:: https://readthedocs.org/projects/spockbot/badge/?version=latest
   :target: https://readthedocs.org/projects/spockbot/?badge=latest
.. _cryptography: https://cryptography.io/
.. _minecraft_data: https://pypi.python.org/pypi/minecraft_data
