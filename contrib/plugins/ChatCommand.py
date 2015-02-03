"""
Just a dumb plugin to let me run !command arguments from ingame to fire off actions
I will probably turn this into a useful generic plugin at some point but for now
its just a testing bed for stuff
"""

from spock.mcp import mcdata
import datetime

class ChatCommandPlugin:
	def __init__(self, ploader, settings):
		self.physics = ploader.requires('Physics')
		self.net = ploader.requires('Net')
		self.inventory = ploader.requires('Inventory')
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
		elif command == 'speak':
			self.net.push_packet('PLAY>Chat Message', {'message': ' '.join(args)})
		elif command == 'date':
			self.net.push_packet('PLAY>Chat Message', {'message': 'Current Date: ' + str(datetime.datetime.now())})
		elif command == 'cmd':
			self.net.push_packet('PLAY>Chat Message', {'message': '/' + ' '.join(args)})
		elif command == 'slot':
			if len(args) == 1 and (int(args[0]) >= 0 and int(args[0]) <= 8):
				self.net.push_packet('PLAY>Held Item Change', {'slot': int(args[0])})
		elif command == 'place':
			#cur_pos_# 0-16
			# we can send held item of -1 and it will work might not be as clean but he still places the object because server side inventories
			block_data = {'location': {'x': int(args[0]),'y': int(args[1]),'z': int(args[2])}, 'direction':1, 'held_item': {'id': -1}, 'cur_pos_x': 8, 'cur_pos_y': 16, 'cur_pos_z': 8}
			print(block_data)
			self.net.push_packet('PLAY>Player Block Placement', block_data)	
		elif command == 'inv':
			self.inventory.test_inventory()

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
