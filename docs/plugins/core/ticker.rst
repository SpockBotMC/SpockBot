.. _plugin-ticker:

******
Ticker
******

Description
===========
.. automodule:: spock.plugins.core.ticker

Events
======
.. object:: action_tick

    This tick is for scheduling physical actions for the client, specifically
    those related to movement. Any plugin that wishes to move the client
    should schedule those movements by hooking into `action_tick` and calling
    the appropriate pathfinding or movement methods.

.. object:: physics_tick

    This tick fires immediately after `action_tick` and signals that all
    movement actions have been scheduled and the client is ready to process
    the movement actions as well as world forces to resolve a position for
    the client. The default PhysicsPlugin depends on this event.

.. object:: client_tick

    This tick fires immediately after `physics_tick` and signals that a new
    position has been resolved for the client and is ready to be sent to the
    server. The default MovementPlugin depends on this event.
