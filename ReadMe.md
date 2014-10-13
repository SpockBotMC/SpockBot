Inspired by remyroy's COPS, a Minecraft client in Python. Protocol implementation based on barneymc

Currently supports jack-diddly-squat because Minecraft 1.8 broke everything

spock
=====

Bot framework, currently under heavy development

Protocol stuff lives in spock/mcp
Map stuff lives in spock/mcmap
Important client stuff lives in spock/plugins/core
Less important stuff lives in spock/plugins/helpers

Client could loosely be called "event-driven", by default plugins register handler functions to handle events that may or may not be emitted by other plugins. Everything is a plugin in spock, including the event loop/framework itself, so you can feel free to rip out the entire back end and replace it with your framework or paradigm of choice. As long as you provide the same simple APIs, other plugins won't know the difference.

Currently writing Spock plugins requires a fairly intricate understanding of the MC protocol, since there aren't many plugins that provide higher abstractions than MC packets. That said the API is starting to shape up quite nicely, we've got threading and the start of a World API. Once Python 3.4 comes out we'll probably try to stablize the event loop API around asyncio and provide some sort of ghetto fallback for older Python 3.x

Speaking of compatibility, Spock runs on Python 3.x on *Nix operating systems, and requires PyCrypto. Theoretically it runs on Windows but no one has ever tested it and I'm fairly sure there are a couple (easy to fix) errors that will
 pop up. Python 2.x would be nice, but it becomes an ever more distant goal as Spock continues to grow dependencies on new Python features. Not impossible, just not a priority

I'll write a real ReadMe and API docs when everything is done and stable-ish.
For now you can check out the plugins folder to get a vague idea of what plugins should look like, find me on #mcdevs or email me at nickelpro@gmail.com if you have questions


###Legal

License is MIT and can be found in license.md

The NBT parser and the original protocol implementation came from other projects,
relevant legal information and attribution can be found in legal.md
