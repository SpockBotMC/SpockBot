SpockBot
=====
[![Build Status](https://travis-ci.org/SpockBotMC/SpockBot.svg)](https://travis-ci.org/SpockBotMC/SpockBot)
[![Coverage Status](https://coveralls.io/repos/SpockBotMC/SpockBot/badge.svg?branch=master&service=github)](https://coveralls.io/github/SpockBotMC/SpockBot?branch=master)

Spock currently supports Minecraft 1.8.8


Bot framework, currently under heavy development

Protocol stuff lives in [spock/mcp](spock/mcp)  
Map stuff lives in [spock/mcmap](spock/mcmap)  
Important client stuff lives in [spock/plugins/core](spock/plugins/core)  
Less important stuff lives in [spock/plugins/helpers](spock/plugins/helpers)  

Client could loosely be called "event-driven", by default plugins register
handler functions to handle events that may or may not be emitted by other
plugins. Everything is a plugin in spock, including the event loop/framework
itself, so you can feel free to rip out the entire back end and replace it with
your framework or paradigm of choice. As long as you provide the same simple
APIs, other plugins won't know the difference.

Currently writing Spock plugins requires a fairly intricate understanding of the
MC protocol, since there aren't many plugins that provide higher abstractions
than MC packets. That said the API is starting to shape up quite nicely, we've
got timers, basic physics, and the beginnings of a World API.

Spock officially supports Python 3.x on \*nix operating systems and requires
PyCrypto. It also runs on Windows and under Python 2.7+ but that's not regularly
tested and might break at any given moment. If you support one of those use
cases and Spock breaks for you, submit an issue with a stack trace and we'll try
to fix it.

##Dependencies

Python 3.x or Python 2.7.x  
PyCrypto

##Installation

`python3 setup.py install`  

##Examples
Refer to the [example bot](examples/basic) for instructions on how to write a bot and a plugin that provides some common functionality.

Also see [Some Useful Examples](https://github.com/SpockBotMC/SpockBot-Contrib/tree/master/examples) for additional examples contributed by the community.

##API Docs
Current API docs live here https://spockbotmc.github.io/docs/spock/

##Support
`#spockbot` on Freenode  
gamingrobot or nickelpro in `#mcdevs` on Freenode

##Credits
Inspired by [remyroy's COPS](http://www.reddit.com/r/Civcraft/comments/13kwjm/introducing_the_cops_civcraft_online_player_status/),
a Minecraft client in Python. Protocol implementation based on [barneymc](https://github.com/barneygale/barneymc)

COPS was a service that tracked players on a minecraft server called Civcraft. It looked like [this](http://i.imgur.com/SR2qII5.jpg)

##Legal

License is MIT and can be found in `LICENSE`

The NBT parser and the original protocol implementation came from other projects,
relevant legal information and attribution can be found in `LEGAL.md`
