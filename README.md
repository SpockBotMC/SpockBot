spock
=====

Inspired by remyroy's COPS, a Minecraft client in Python. Protocol implementation based on barneymc

Protocol stuff lives in spock/mcp

Client stuff lives in spock/net

Client could loosely be called "event-driven", plugins should register "dispatchers" to be called to handle specific packets.
Plugins can also register callbacks to extend the event loop and implement behavior based on event flags.

I'll write a real ReadMe and API docs when everything is done and stable-ish.
For now you can check out the plugins folder to get a vague idea of what plugins should look like, find me on #mcdevs if you have questions
