from spock.mcp import mcdata

class ChatCommandPlugin:
	def __init__(self, ploader, settings):
		self.physics = ploader.requires('Physics')
		ploader.reg_event_handler(
			'PLAY<Chat Message', self.handle_chat_message
		)

	def handle_chat_message(self, name, packet):
		chat_data = packet.data['json_data']
		message = self.parse_chat(chat_data)
		try:
			command = message[message.index('!'):]
			spacepos = command.find(' ')
			if spacepos == -1: #no arguments
				command = command[1:]
			else: #have arguments, for now just ignore them
				command = command[1:spacepos]
			self.command_handle(command.strip(), [])
		except ValueError: #not a command so just move along
			pass

	def command_handle(self, command, args):
		print("Command:", command)
		if command == 'jump' or command == 'j':
			self.physics.jump()

	def parse_chat(self, chat_data):
		message = ''
		if type(chat_data) is dict:
			if 'text' in chat_data:
				message += chat_data['text']
				if 'extra' in chat_data:
					message += self.parse_chat(chat_data['extra'])
			elif 'translate' in chat_data:
				if 'with' in chat_data:
					message += self.parse_chat(chat_data['with'])
		elif type(chat_data) is list:
			for text in chat_data:
				if type(text) is str:
					message += text
				elif type(text) is dict:
					message += self.parse_chat(text)
		return message
