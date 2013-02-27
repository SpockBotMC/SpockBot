Inspired by remyroy's COPS, a Minecraft client in Python. Protocol implementation based on barneymc

spock
=====

Bot framework, currently under heavy development

Protocol stuff lives in spock/mcp  
Client stuff lives in spock/net

Client could loosely be called "event-driven", plugins should register "dispatchers" to be called to handle specific packets and "handlers" to handle flags (In practice mostly socket errors and hangups)

In comparison to other popular MC bots like Mineflayer Spock is much more "bare-bones", in that Spock expects plugins to understand and send packets on their own. The default handlers only mirror Keep Alives and Position Updates from the server (without which the bot would get kicked and be unable to move, respectively). This means that writing Spock plugins require a fairly intricate understanding of the MC protocol. Eventually a more friendly API will be built by extending the Client class provided by Spock but that's awhile off.

I'll write a real ReadMe and API docs when everything is done and stable-ish.
For now you can check out the plugins folder to get a vague idea of what plugins should look like, find me on #mcdevs if you have questions

##spockd

A daemon for spinning up bots, can be controlled with spockctl. Currently under heavy development

##riker

A client that extends spock (is planned) to provide several useful features such as a pathfinding/movement API, as well as services like automatic session keep alives

###Legal

License is MIT and can be found in license.md

The NBT parser, Minecraft.net login function, and most of the Protocol implementation come from other projects, 
relevant legal information and attribution can be found in legal.md
