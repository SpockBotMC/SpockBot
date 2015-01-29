Inspired by [remyroy's COPS](http://www.reddit.com/r/Civcraft/comments/13kwjm/introducing_the_cops_civcraft_online_player_status/),
a Minecraft client in Python. Protocol implementation based on barneymc

Spock currently supports Minecraft 1.8.1

spock
=====

Bot framework, currently under heavy development

Examples live in [contrib/examples](contrib/examples)  
Higher level plugins live in [contrib/plugins](contrib/plugins)  
Protocol stuff lives in [spock/mcp](spcok/mcp)  
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

Spock officially supports Python 3.x on \*Nix operating systems and requires
PyCrypto. It also runs on Windows and under Python 2.7+ but that's not regularly
tested and might break at any given moment. If you support one of those use
cases and Spock breaks for you, submit an issue with a stack trace and we'll try
to fix it.

I'll write a real ReadMe and API docs when everything is done and stable-ish.
For now you can check out the contrib/plugins folder to get a vague idea of what
plugins should look like, find me on #mcdevs or email me at nickelpro@gmail.com
if you have questions'

##Dependencies

Python 3.x or Python 2.7+  
PyCrypto 

##Installation

`python setup.py install`  
Depending on your distro it will be `python3 setup.py install` 

##Example
[Demo](contrib/examples/demo.py)

##API Docs
Current API docs live here https://nickelpro.github.io/spock/docs/spock/

##Legal

License is MIT and can be found in LICENSE

The NBT parser and the original protocol implementation came from other projects,
relevant legal information and attribution can be found in LEGAL.md

#####P.S.
A lot of people ask what COPS was. It was a service that tracked players on a
minecraft server called Civcraft. It looked like [this](http://www.nickg.org/dl/cops.jpg)
