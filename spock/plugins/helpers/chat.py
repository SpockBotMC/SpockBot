import logging

from six import string_types

from spock.plugins.base import PluginBase
from spock.utils import pl_announce

logger = logging.getLogger('spock')


translations = {}
try:
    with open('en_US.lang', 'r') as trf:
        for line in trf:
            if '=' in line:
                # cut off newline, split some.translation.id=format %s string
                translation_id, format_str = line[:-1].split('=', 1)
                translations[translation_id] = format_str
except:
    logger.warn('en_US.lang not loaded, cannot translate chat messages')


class ChatParseError(Exception):
    pass


def parse_with_1_extra(json_data):
    if json_data['translate'] not in ():
        raise ChatParseError
    return str(''.join(json_data['with'][1]['extra']))


@pl_announce('Chat')
class ChatPlugin(PluginBase):
    """
    Emits `chat` events with `{position, raw, text, type, message, name, uuid}`

    <sort> is None or one of:
    achievement, admin, announcement, emote, incoming, outgoing, text

    If <sort> is not None, <name>, <uuid>, <message> are set and an additional
    `chat_<sort>` event is emitted.

    `uuid` contains dashes and is Null if not present.
    """

    requires = 'Event'
    events = {'PLAY<Chat Message': 'handle_chat'}

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
        try:  # always at the same place if present
            uuid = json_data['with'][0]['hoverEvent']['value'][5:41]
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
                    translate_fmt = translations[translate_id]
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
