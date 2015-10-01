.. _plugin-clientinfo:

***********
Client Info
***********

Description
===========
.. automodule:: spock.plugins.helpers.clientinfo

Events
======
.. object:: client_login_success

    Client Info is done processing the Login Success packet

.. object:: client_join_game

    Client Info is done processing the Join Game packet

    **Payload** ::

        GameInfo()

.. object:: client_spawn_update

    Client Info is done processing the Spawn Position packet

    **Payload** ::

        Position()

.. object:: client_health_update

    When the players health changes

    **Payload** ::

        PlayerHealth()

.. object:: client_death

    When the player health becomes 0.0

    **Payload** ::

        PlayerHealth()

.. object:: client_position_update

    When the player is moved by the server

    **Payload** ::

        PlayerPosition()

.. object:: client_add_player

    Player added to the player list

    **Payload** ::

        PlayerListItem()

.. object:: client_update_player

    Player info is updated on the player list

    **Payload** ::

        PlayerListItem()

.. object:: client_remove_player

    Player removed from the player list

    **Payload** ::

        PlayerListItem()

Methods and Attributes
======================
.. autoclass:: ClientInfo
    :members:
    :undoc-members:
