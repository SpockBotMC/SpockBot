"""Processes chat into easy to use events"""

import logging

from six import string_types

from spockbot.plugins.base import PluginBase, pl_announce

logger = logging.getLogger('spockbot')


class ChatParseError(Exception):
    pass


def parse_with_1_extra(json_data):
    if json_data['translate'] not in ():
        raise ChatParseError
    return str(''.join(json_data['with'][1]['extra']))


class ChatCore(object):
    def __init__(self, net):
        self.net = net

    def chat(self, message):
        for line in message.split('\n'):
            while line:
                part, line = line[:100], line[100:]
                self.net.push_packet('PLAY>Chat Message', {'message': part})

    def whisper(self, player, message):
        self.chat('/tell %s %s' % (player, message))


@pl_announce('Chat')
class ChatPlugin(PluginBase):
    """
    Emits ``chat`` events with
    ``position, raw, text, type, message, name, uuid``.

    ``position``: Always one of ``spockbot.mcdata.constants``'s
    ``CHAT_POS_CHAT, CHAT_POS_SYSTEM_MESSAGE, CHAT_POS_ABOVE_HOTBAR``.

    ``raw``: Always the JSON dict as received from the server.

    ``text``: The text (without formatting) of the chat message
    as the vanilla client would display it.
    Needs ``en_US.lang`` to be present in the active directory,
    otherwise some but not all messages are translated properly.

    ``type``: None or one of
    ``achievement, admin, announcement, emote, incoming, outgoing, text``,
    which are the last part of the corresponding vanilla translation IDs.

    If ``type`` is not None, ``message, name, uuid`` are set and an
    additional ``chat_<type>`` event is emitted.
    Otherwise, ``message, name, uuid`` are all None.

    ``message``: The message as it was typed by the sender.

    ``name``: The name of the sender.

    ``uuid``: The UUID of the sender, with dashes.
    """

    requires = ('Event', 'Net')
    events = {'PLAY<Chat Message': 'handle_chat'}

    def __init__(self, ploader, settings):
        super(ChatPlugin, self).__init__(ploader, settings)
        self.chatcore = ChatCore(self.net)
        ploader.provides('Chat', self.chatcore)
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        try:
            with open('en_US.lang', 'r') as lang_file:
                # the chat data comes in as strings, so we need to
                # replace all %d, %i, %3$d etc. with %s
                import re
                pcts_only = re.compile('%([0-9]\$)?[a-z]')
                for line in lang_file:
                    if '=' in line:
                        # cut off newline, split some.
                        # translation.id=format %s string
                        trans_id, format_str = line[:-1].split('=', 1)
                        self.translations[trans_id] = pcts_only.sub('%s',
                                                                    format_str)
        except:
            logger.warn('CHAT: en_US.lang not loaded, '
                        'cannot translate chat messages')

    def handle_chat(self, evt, packet):
        position = packet.data['position']  # where is the text displayed?
        json_data = packet.data['json_data']  # raw data from server

        # the text as the vanilla client displays it
        # note that on a vanilla server, this uses the `translations` dict
        text = self.render_chat(json_data)

        parseable_translate_ids = ('chat.type', 'commands.message.display')

        # significant (last) part of the chat's 'translate' ID
        chat_type = None
        if 'translate' in json_data:
            # only use last id part if significant
            a, b = json_data['translate'].rsplit('.', 1)  # TODO var names :P
            if a in parseable_translate_ids:
                chat_type = b

        # the message typed by the sender
        try:
            if json_data['translate'].startswith(parseable_translate_ids):
                msg = json_data['with'][1]
                if isinstance(msg, dict):
                    msg = msg.get('text', '') + ''.join(msg.get('extra', ''))
            else:
                msg = None
        except (IndexError, KeyError, TypeError):
            msg = None

        # sender name
        try:  # always at the same place if present
            name = json_data['with'][0]
            if isinstance(name, dict):
                name = name.get('text', '') + ''.join(name.get('extra', ''))
        except (IndexError, KeyError, TypeError):
            name = None

        # sender UUID
        try:
            text_with_uuid = json_data['with'][0]['hoverEvent']['value']
            uuid = text_with_uuid[text_with_uuid.index('id:"'):][4:40]
        except (IndexError, KeyError, TypeError):
            uuid = None

        event_data = {
            'position': position, 'raw': json_data, 'text': text,
            'type': chat_type, 'message': msg, 'name': name, 'uuid': uuid,
        }
        if chat_type:
            self.event.emit('chat_%s' % chat_type, event_data)
        self.event.emit('chat', event_data)

    def render_chat(self, chat_data):
        """
        Render the text as in the vanilla client.
        On a vanilla server, this uses the translations dict.
        """
        if isinstance(chat_data, dict):
            if 'text' in chat_data:
                message = chat_data['text']
            elif 'translate' in chat_data:
                translate_id = chat_data['translate']
                args = tuple(map(self.render_chat, chat_data.get('with', [])))
                try:
                    translate_fmt = self.translations[translate_id]
                    message = translate_fmt % args
                except KeyError:  # could not find translate_id
                    message = '<"%s" %s>' % (translate_id, args)
                except TypeError:  # format does not match args
                    logger.error('Translate failed to format "%s" with %s',
                                 translate_fmt, args)
                    message = '<"%s" %s>' % (translate_fmt, args)
            else:  # not implemented
                message = '<%s>' % chat_data
            if 'extra' in chat_data:
                message += ''.join(self.render_chat(extra)
                                   for extra in chat_data['extra']
                                   if isinstance(extra, (dict, string_types)))
            return message
        elif isinstance(chat_data, list):
            raise NotImplementedError
        else:  # string or number etc.
            return chat_data
