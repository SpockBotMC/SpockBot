from spock.mcp import mcdata

class ChatCommandPlugin:
	def __init__(self, ploader, settings):
		self.physics = ploader.requires('Physics')
		self.net = ploader.requires('Net')
		self.clinfo = ploader.requires('ClientInfo')
		ploader.reg_event_handler(
			'PLAY<Chat Message', self.handle_chat_message
		)

	def handle_chat_message(self, name, packet):
		chat_data = packet.data['json_data']
		message = self.parse_chat(chat_data)
		print('Chat:', message)
		try:
			command = message[message.index('!'):]
			args = []
			spacepos = command.find(' ')
			if spacepos == -1: #no arguments
				command = command[1:]
			else: #have arguments
				args = command[spacepos+1:].split(' ')
				command = command[1:spacepos]
			self.command_handle(command.strip(), args)
		except ValueError: #not a command so just move along
			pass

	def command_handle(self, command, args):
		if command == '':
			return
		print("Command:", command)
		if command == 'jump' or command == 'j':
			self.physics.jump()
		elif command == 'say':
			#self.net.push_packet('PLAY>Chat Message', {'message': ' '.join(args)})
			pass
		elif command == 'cmd':
			self.net.push_packet('PLAY>Chat Message', {'message': '/' + ' '.join(args)})
		elif command == 'slot':
			if len(args) == 1 and (int(args[0]) >= 0 and int(args[0]) <= 8):
				self.net.push_packet('PLAY>Held Item Change', {'slot': int(args[0])})
		elif command == 'place':
			block_data = {'location': {'x': int(self.clinfo.position['x']),'y': int(self.clinfo.position['y']),'z': int(self.clinfo.position['z'])}, 'direction':chr(0), 'held_item': 0, 'cur_pos_x': chr(1), 'cur_pos_y': chr(1), 'cur_pos_z': chr(1)}
			print(block_data)
			self.net.push_packet('PLAY>Player Block Placement', block_data)	

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
