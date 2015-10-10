.. _plugin-chat:

****
Chat
****

Description
===========
.. automodule:: spockbot.plugins.helpers.chat

Events
======
.. object:: chat

    Chat event was recieved 

    **Playload** ::

        {'position': position, 'raw': json_data, 'text': text, 'type': chat_type, 'message': msg, 'name': name, 'uuid': uuid}

    .. object:: position

        *int*

        Where the text should be displayed

    .. object:: raw

        *dict*

        Raw json data from the chat message

    .. object:: text

        *string*

        The text of the chat message

    .. object:: type

        *string*

        The type of message (achievement, admin, announcement, emote, incoming, outgoing, text)

    .. object:: message

        *string*

        message

    .. object:: uuid

        *string*

        UUID of the player who sent the message


Methods and Attributes
======================
.. autoclass:: ChatCore
    :members:
    :undoc-members:


