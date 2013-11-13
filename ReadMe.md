Inspired by remyroy's COPS, a Minecraft client in Python. Protocol implementation based on barneymc
Currently Supports Minecraft 1.7.2

spock
=====

Bot framework, currently under heavy development

Protocol stuff lives in spock/mcp  
Client stuff lives in spock/net

Client could loosely be called "event-driven", plugins register handler functions to handle specific packets and flags (In practice mostly socket errors and hangups)

In comparison to other popular MC bots like Mineflayer Spock is much more "bare-bones", in that Spock expects plugins to understand and send packets on their own. The default handlers only mirror Keep Alives and Position Updates from the server (without which the bot would get kicked and be unable to move, respectively). This means that writing Spock plugins require a fairly intricate understanding of the MC protocol.

I'll write a real ReadMe and API docs when everything is done and stable-ish.
For now you can check out the plugins folder to get a vague idea of what plugins should look like, find me on #mcdevs if you have questions


###Legal

License is MIT and can be found in license.md

The NBT parser, Minecraft.net login function, and most of the Protocol implementation come from other projects, 
relevant legal information and attribution can be found in legal.md
