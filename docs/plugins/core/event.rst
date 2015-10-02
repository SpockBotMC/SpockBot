.. _plugin-event:

*****
Event
*****

Description
===========
.. automodule:: spock.plugins.core.event

Events
======
.. object:: event_start

    Fired before the first iteration of the event loop. The default
    StartPlugin depends on this event.

.. object:: event_tick

    Fired at the beginning of every iteration of the event loop. The default
    NetPlugin depends on this event.

.. object:: event_kill

    Fired after the last iteration of the event loop. Many plugins depend on
    this event for environment clean up purposes.

Methods and Attributes
======================
.. autoclass:: EventCore
    :members:
    :undoc-members:
