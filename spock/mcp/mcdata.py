#Most of the data formats, structures, and magic values

MC_PROTOCOL_VERSION = 4

SERVER_TO_CLIENT    = 0x00
CLIENT_TO_SERVER    = 0x01

HANDSHAKE_STATE     = 0x00
STATUS_STATE        = 0x01
LOGIN_STATE         = 0x02
PLAY_STATE          = 0x03

data_types = {
	'bool'  : ('?', 1),
	'ubyte' : ('B', 1),
	'byte'  : ('b', 1),
	'ushort': ('H', 2),
	'short' : ('h', 2),
	'uint'  : ('I', 4),
	'int'   : ('i', 4),
	'long'  : ('q', 8),
	'float' : ('f', 4),
	'double': ('d', 8),
}

#Structs formatted for readibility
#Packed into tuples at end of file
packet_names = {
	HANDSHAKE_STATE: {
		SERVER_TO_CLIENT: {},
		CLIENT_TO_SERVER: {
			0x00: 'Handshake',
		},
	},

	STATUS_STATE: {
		SERVER_TO_CLIENT: {
			0x00: 'Status Response',
			0x01: 'Status Ping',
		},
		CLIENT_TO_SERVER: {
			0x00: 'Status Request',
			0x01: 'Status Ping',
		},
	},

	LOGIN_STATE: {
		SERVER_TO_CLIENT: {
			0x00: 'Disconnect',
			0x01: 'Encryption Request',
			0x02: 'Login Success',
		},
		CLIENT_TO_SERVER: {
			0x00: 'Login Start',
			0x01: 'Encryption Response',
		},
	},

	PLAY_STATE: {
		SERVER_TO_CLIENT: {
			0x00: 'Keep Alive',
			0x01: 'Join Game',
			0x02: 'Chat Message',
			0x03: 'Time Update',
			0x04: 'Entity Equipment',
			0x05: 'Spawn Position',
			0x06: 'Update Health',
			0x07: 'Respawn',
			0x08: 'Player Position and Look',
			0x09: 'Held Item Change',
			0x0A: 'Use Bed',
			0x0B: 'Animation',
			0x0C: 'Spawn Player',
			0x0D: 'Collect Item',
			0x0E: 'Spawn Object',
			0x0F: 'Spawn Mob',
			0x10: 'Spawn Painting',
			0x11: 'Spawn Experience Orb',
			0x12: 'Entity Velocity',
			0x13: 'Destroy Entities',
			0x14: 'Entity',
			0x15: 'Entity Relative Move',
			0x16: 'Entity Look',
			0x17: 'Entity Look and Relative Move',
			0x18: 'Entity Teleport',
			0x19: 'Entity Head Look',
			0x1A: 'Entity Status',
			0x1B: 'Attach Entity',
			0x1C: 'Entity Metadata',
			0x1D: 'Entity Effect',
			0x1E: 'Remove Entity Effect',
			0x1F: 'Set Experience',
			0x20: 'Entity Properties',
			0x21: 'Chunk Data',
			0x22: 'Multi Block Change',
			0x23: 'Block Change',
			0x24: 'Block Action',
			0x25: 'Block Break Animation',
			0x26: 'Map Chunk Bulk',
			0x27: 'Explosion',
			0x28: 'Effect',
			0x29: 'Sound Effect',
			0x2A: 'Particle',
			0x2B: 'Change Game State',
			0x2C: 'Spawn Global Entity',
			0x2D: 'Open Window',
			0x2E: 'Close Window',
			0x2F: 'Set Slot',
			0x30: 'Window Items',
			0x31: 'Window Property',
			0x32: 'Confirm Transaction',
			0x33: 'Update Sign',
			0x34: 'Maps',
			0x35: 'Update Block Entity',
			0x36: 'Sign Editor Open',
			0x37: 'Statistics',
			0x38: 'Player List Item',
			0x39: 'Player Abilities',
			0x3A: 'Tab-Complete',
			0x3B: 'Scoreboard Objective',
			0x3C: 'Update Score',
			0x3D: 'Display Scoreboard',
			0x3E: 'Teams',
			0x3F: 'Plugin Message',
			0x40: 'Disconnect',
		},

		CLIENT_TO_SERVER: {
			0x00: 'Keep Alive',
			0x01: 'Chat Message',
			0x02: 'Use Entity',
			0x03: 'Player',
			0x04: 'Player Position',
			0x05: 'Player Look',
			0x06: 'Player Position and Look',
			0x07: 'Player Digging',
			0x08: 'Player Block Placement',
			0x09: 'Held Item Change',
			0x0A: 'Animation',
			0x0B: 'Entity Action',
			0x0C: 'Steer Vehicle',
			0x0D: 'Close Window',
			0x0E: 'Click Window',
			0x0F: 'Confirm Transaction',
			0x10: 'Creative Inventory Action',
			0x11: 'Enchant Item',
			0x12: 'Update Sign',
			0x13: 'Player Abilities',
			0x14: 'Tab-Complete',
			0x15: 'Client Settings',
			0x16: 'Client Status',
			0x17: 'Plugin Message',
		},
	},
}

packet_structs = {
	HANDSHAKE_STATE: {
		SERVER_TO_CLIENT: {
			#Empty, server doesn't handshake
		},
		CLIENT_TO_SERVER: {
			#Handshake
			0x00: (
				('varint', 'protocol_version'),
				('string', 'host'),
				('ushort', 'port'),
				('varint', 'next_state'),
			),
		},
	},

	STATUS_STATE: {
		SERVER_TO_CLIENT: {
			#Status Response
			0x00: (
				('string', 'json_response'),
			),
			#Status Ping
			0x01: (
				('long', 'time'),
			),
		},
		CLIENT_TO_SERVER: {
			#Status Request
			0x00: (
				#Empty Packet
			),
			#Status Ping
			0x01: (
				('long', 'time'),
			),
		},
	},

	LOGIN_STATE: {
		SERVER_TO_CLIENT: {
			#Disconnect
			0x00: (
				('string', 'json_data'),
			),
			#Encryption Request
			0x01: (
				('string', 'server_id'),
				#Extension
					#byte string 'public_key'
					#byte string 'verify_token'
			),
			#Login Success
			0x02: (
				('string', 'uuid'),
				('string', 'username'),
			),
		},
		CLIENT_TO_SERVER: {
			#Login Start
			0x00: (
				('string', 'name'),
			),
			#Encryption Response
			0x01: (
				#Extension
					#byte string 'shared_secret'
					#byte string 'verify token'
			),
		},
	},

	PLAY_STATE: {
		SERVER_TO_CLIENT: {
			#Keep Alive
			0x00: (
				('int', 'keep_alive'),
			),
			#Join Game
			0x01: (
				('int'   , 'eid'),
				('ubyte' , 'gamemode'),
				('byte'  , 'dimension'),
				('ubyte' , 'difficulty'),
				('ubyte' , 'max_players'),
				('string', 'level_type'),
			),
			#Chat Message
			0x02: (
				('string', 'json_data'),
			),
			#Time Update
			0x03: (
				('long', 'world_age'),
				('long', 'time_of_day'),
			),
			#Entity Equipment
			0x04: (
				('int'  , 'eid'),
				('short', 'slot'),
				('slot' , 'item'),
			),
			#Spawn Position
			0x05: (
				('int', 'x'),
				('int', 'y'),
				('int', 'z'),
			),
			#Update Health
			0x06: (
				('float', 'health'),
				('short', 'food'),
				('float', 'saturation'),
			),
			#Respawn
			0x07: (
				('int'   , 'dimension'),
				('ubyte' , 'difficulty'),
				('ubyte' , 'gamemode'),
				('string', 'level_type'),
			),
			#Player Position and Look
			0x08: (
				('double', 'x'),
				('double', 'y'),
				('double', 'z'),
				('float' , 'yaw'),
				('pitch' , 'float'),
				('bool'  , 'on_ground'),
			),
			#Held Item Change
			0x09: (
				('byte', 'slot'),
			),
			#Use Bed
			0x0A: (
				('int'  , 'eid'),
				('int'  , 'x'),
				('ubyte', 'y'),
				('int'  , 'z')
			),
			#Animation
			0x0B: (
				('varint', 'eid'),
				('ubyte' , 'animation'),
			),
			#Spawn Player
			0x0C: (
				('varint', 'eid'),
				('string', 'player_uuid'),
				('string', 'player_name'),
				('int'   , 'x'),
				('int'   , 'y'),
				('int'   , 'z'),
				('byte'  , 'yaw'),
				('byte'  , 'pitch'),
				('short' , 'current_item'),
				('metadata', 'metadata'),
			),
			#Collect Item
			0x0D: (
				('int', 'collected_eid'),
				('int', 'collector_eid'),
			),
			#Spawn Object
			0x0E: (
				('varint', 'eid'),
				('ubyte' , 'type'),
				('int'   , 'x'),
				('int'   , 'y'),
				('int'   , 'z'),
				('byte'  , 'pitch'),
				('byte'  , 'yaw'),
				('int'   , 'obj_data')
				#Extension
					#If obj_data != 0
					#short 'speed_x'
					#short 'speed_y'
					#short 'speed_z'
			),
			#Spawn Mob
			0x0F: (
				('varint', 'eid'),
				('ubyte' , 'type'),
				('int'   , 'x'),
				('int'   , 'y'),
				('int'   , 'z'),
				('byte'  , 'pitch'),
				('byte'  , 'head_pitch'),
				('byte'  , 'yaw'),
				('short' , 'velocity_x'),
				('short' , 'velocity_y'),
				('short' , 'velocity_z'),
				('metadata', 'metadata'),
			),
			#Spawn Painting
			0x10: (
				('varint', 'eid'),
				('string', 'title'),
				('int'   , 'x'),
				('int'   , 'y'),
				('int'   , 'z'),
				('int'   , 'direction'),
			),
			#Spawn Experience Orb
			0x11: (
				('varint', 'eid'),
				('ubyte' , 'type'),
				('int'   , 'x'),
				('int'   , 'y'),
				('int'   , 'z'),
				('short' , 'count'),
			),
			#Entity Velocity
			0x12: (
				('int'  , 'eid'),
				('short', 'velocity_x'),
				('short', 'velocity_y'),
				('short', 'velocity_z'),
			),
			#Destroy Entities
			0x13: (
				#Extension
					#List of ints 'eids'
			),
			#Entity
			0x14: (
				('int', 'eid'),
			),
			#Entity Relative Move
			0x15: (
				('int' , 'eid'),
				('byte', 'dx'),
				('byte', 'dy'),
				('byte', 'dz'),
			),
			#Entity Look
			0x16: (
				('int' , 'eid'),
				('byte', 'yaw'),
				('byte', 'pitch'),
			),
			#Entity Look and Relative Move
			0x17: (
				('int' , 'eid'),
				('byte', 'dx'),
				('byte', 'dy'),
				('byte', 'dz'),
				('byte', 'yaw'),
				('byte', 'pitch'),
			),
			#Entity Teleport
			0x18: (
				('int' , 'eid'),
				('int' , 'x'),
				('int' , 'y'),
				('int' , 'z'),
				('byte', 'yaw'),
				('byte', 'pitch'),
			),
			#Entity Head Look
			0x19: (
				('int' , 'eid'),
				('byte', 'head_yaw'),
			),
			#Entity Status
			0x1A: (
				('int' , 'eid'),
				('byte', 'status')
			),
			#Attach Entity
			0x1B: (
				('int' , 'eid'),
				('int' , 'v_eid'),
				('bool', 'leash'),
			),
			#Entity Metadata
			0x1C: (
				('int', 'eid'),
				('metadata', 'metadata')
			),
			#Entity Effect
			0x1D: (
				('int'  , 'eid'),
				('byte' , 'effect'),
				('byte' , 'amplifier'),
				('short', 'duration'),
			),
			#Remove Entity Effect
			0x1E: (
				('int' , 'eid'),
				('byte', 'effect'),
			),
			#Set Experience
			0x1F: (
				('float', 'exp_bar'),
				('short', 'level'),
				('short', 'total_exp'),
			),
			#Entity Properties
			0x20: (
				('int', 'eid'),
				#Extension
					#List of dicts 'properties'
					#Entity properties are complex beasts
					#Consult the decoder to get all of the keys
			),
			#Chunk Data
			0x21: (
				('int'   , 'chunk_x'),
				('int'   , 'chunk_z'),
				('bool'  , 'continuous'),
				('ushort', 'primary_bitmap'),
				('ushort', 'add_bitmap'),
				#Extension
					#byte string 'data'
			),
			#Multi Block Change
			0x22: (
				('int'  , 'chunk_x'),
				('int'  , 'chunk_z'),
				#Extension
					#List of dicts 'blocks'
			),
			#Block Change
			0x23: (
				('int'   , 'x'),
				('ubyte' , 'y'),
				('int'   , 'z'),
				('varint', 'block_id'),
				('ubyte' , 'metadata'),
			),
			#Block Action
			0x24: (
				('int'   , 'x'),
				('short' , 'y'),
				('int'   , 'z'),
				('ubyte' , 'byte_1'),
				('ubyte' , 'byte_2'),
				('varint', 'block_id'),
			),
			#Block Break Animation
			0x25: (
				('varint', 'eid'),
				('int'   , 'x'),
				('int'   , 'y'),
				('int'   , 'z'),
				('byte'  , 'stage'),
			),
			#Map Chunk Bulk
			0x26: (
				# 'sky_light' is stuck in the middle of
				# the packet, so it's easier to handle
				# it in an extension
				#Extension
					#bool 'sky_light'
					#byte string 'data'
					#List of dicts 'metadata'
					#Metadata is identical to 0x21
					#But the 'continuous' bool is assumed True
			),
			#Explosion
			0x27: (
				('float', 'x'),
				('float', 'y'),
				('float', 'z'),
				('float', 'radius'),
				# 'player_%' fields at end of packet for
				# some reason, easier to handle in extension
				#Extension
					#List of lists 'blocks'
					#Each list is 3 ints x,y,z
					#float 'player_x'
					#float 'player_y'
					#float 'player_z'
			),
			#Effect
			0x28: (
				('int' , 'effect'),
				('int' , 'x'),
				('byte', 'y'),
				('int' , 'z'),
				('int' , 'data'),
				('bool', 'no_rel_vol'),
			),
			#Sound Effect
			0x29: (
				('string', 'name'),
				('int'   , 'ef_x'),
				('int'   , 'ef_y'),
				('int'   , 'ef_z'),
				('float' , 'vol'),
				('ubyte' , 'pitch'),
			),
			#Particle
			0x2A: (
				('string', 'name'),
				('float' , 'x'),
				('float' , 'y'),
				('float' , 'z'),
				('float' , 'off_x'),
				('float' , 'off_y'),
				('float' , 'off_z'),
				('float' , 'speed'),
				('float' , 'num'),
			),
			#Change Game State
			0x2B: (
				('ubyte', 'reason'),
				('float', 'value'),
			),
			#Spawn Global Entity
			0x2C: (
				('varint', 'eid'),
				('byte', 'type'),
				('int' , 'x'),
				('int' , 'y'),
				('int' , 'z'),
			),
			#Open Window
			0x2D: (
				('ubyte' , 'window_id'),
				('ubyte' , 'inv_type'),
				('string', 'title'),
				('ubyte' , 'slot_count'),
				('bool'  , 'use_title'),
				('int'   , 'eid'),
			),
			#Close Window
			0x2E: (
				('ubyte', 'window_id'),
			),
			#Set Slot
			0x2F: (
				('ubyte', 'window_id'),
				('short', 'slot'),
				('slot' , 'slot_data'),
			),
			#Window Items
			0x30: (
				('ubyte', 'window_id'),
				#Extension
					#List of slots 'slots'
			),
			#Window Property
			0x31: (
				('ubyte', 'window_id'),
				('short', 'property'),
				('short', 'value'),
			),
			#Confirm Transaction
			0x32: (
				('ubyte', 'window_id'),
				('short', 'action'),
				('bool' , 'accepted'),
			),
			#Update Sign
			0x33: ( 
				('int'   , 'x'),
				('short' , 'y'),
				('int'   , 'z'),
				('string', 'line_1'),
				('string', 'line_2'),
				('string', 'line_3'),
				('string', 'line_4'),
			),
			#Maps
			0x34: (
				('varint', 'item_damage'),
				#Extension
					#byte string 'data'
			),
			#Update Block Entity
			0x35: (
				('int'   , 'x'),
				('short' , 'y'),
				('int'   , 'z'),
				('ubyte' , 'action'),
				#Extension
					#NBT Data 'nbt'
			),
			#Sign Editor Open
			0x36: (
				('int'   , 'x'),
				('int'   , 'y'),
				('int'   , 'z'),
			),
			#Statistics
			0x37: (
				#Extension
					#List of lists 'entries'
					#First value is a string, stat's name
					#Second value is an int, stat's value
			),
			#Player List Item
			0x38: (
				('string', 'player_name'),
				('bool'  , 'online'),
				('short' , 'ping'),

			),
			#Player Abilities
			0x39: (
				('byte', 'flags'),
				('float', 'flying_speed'),
				('float', 'walking_speed'),
			),
			#Tab-Complete
			0x3A: (
				#Extension
					#List of strings 'matches'
			),
			#Scoreboard Objective
			0x3B: (
				('string', 'obj_name'),
				('string', 'obj_val'),
				('byte'  , 'action'),
			),
			#Update Score
			0x3C: (
				('string', 'item_name'),
				('byte'  , 'action'),
				('string', 'score_name'),
				('int'   , 'value'),
			),
			#Display Scoreboard
			0x3D: (
				('byte'  , 'position'),
				('string', 'score_name'),
			),
			#Teams
			0x3E: (
				('string', 'team_name'),
				('byte'  , 'mode'),
				#Extension
					#Depends on mode
					#0 gets all fields
					#1 gets no fields
					#For 2:
						#string 'display_name'
						#string 'team_prefix'
						#string 'team_suffix'
						#byte 'friendly_fire'
					#For 3 or 4:
						# List of strings 'players'
			),
			#Plugin Message
			0x3F: (
				('string', 'channel'),
				#Extension
					#byte string 'data'
			),
			#Disconnect
			0x40: (
				('string', 'reason'),
			),
		},

		CLIENT_TO_SERVER: {
			#Keep Alive
			0x00: (
				('int', 'keep_alive'),
			),
			#Chat Message
			0x01: (
				('string', 'message'),
			),
			#Use Entity
			0x02: (
				('int' , 'target'),
				('byte', 'mouse'),
			),
			#Player
			0x03: (
				('bool', 'on_ground'),
			),
			#Player Position
			0x04: (
				('double', 'x'),
				('double', 'stance'),
				('double', 'y'),
				('double', 'z'),
				('bool'  , 'on_ground'),
			),
			#Player Look
			0x05: (
				('float', 'yaw'),
				('float', 'pitch'),
				('bool' , 'on_ground'),
			),
			#Player Position and Look
			0x06: (
				('double', 'x'),
				('double', 'stance'),
				('double', 'y'),
				('double', 'z'),
				('float', 'yaw'),
				('float', 'pitch'),
				('bool' , 'on_ground'),
			),
			#Player Digging
			0x07: (
				('byte' , 'status'),
				('int'  , 'x'),
				('ubyte', 'y'),
				('int'  , 'z'),
				('byte' , 'face'),
			),
			#Player Block Placement
			0x08: (
				('int'  , 'x'),
				('ubyte', 'y'),
				('int'  , 'z'),
				('byte' , 'direction'),
				('slot' , 'held_item'),
				('byte' , 'cur_pos_x'),
				('byte' , 'cur_pos_y'),
				('byte' , 'cur_pos_z'),
			),
			#Held Item Change
			0x09: (
				('short', 'slot'),
			),
			#Animation
			0x0A: (
				('int', 'eid'),
				('byte', 'animation'),
			),
			#Entity Action
			0x0B: (
				('int' , 'eid'),
				('byte', 'action'),
				('int' , 'jump_boost'),
			),
			#Steer Vehicle
			0x0C: (
				('float', 'sideways'),
				('float', 'forward'),
				('bool' , 'jump'),
				('bool' , 'unmount'),
			),
			#Close Window
			0x0D: (
				('byte', 'window_id'),
			),
			#Click Window
			0x0E: (
				('byte' , 'window_id'),
				('short', 'slot'),
				('byte' , 'button'),
				('short', 'action'),
				('byte' , 'mode'),
				('slot' , 'clicked_item'),
			),
			#Confirm Transaction
			0x0F: (
				('byte' , 'window_id'),
				('short', 'action'),
				('bool' , 'accepted'),
			),
			#Creative Inventory Action
			0x10: (
				('short', 'slot'),
				('slot' , 'clicked_item'),
			),
			#Enchant Item
			0x11: (
				('byte', 'window_id'),
				('byte', 'enchantment'),
			),
			#Update Sign
			0x12: (
				('int'   , 'x'),
				('short' , 'y'),
				('int'   , 'z'),
				('string', 'line_1'),
				('string', 'line_2'),
				('string', 'line_3'),
				('string', 'line_4'),
			),
			#Player Abilities
			0x13: (
				('byte', 'flags'),
				('float', 'flying_speed'),
				('float', 'walking_speed'),
			),
			#Tab-Complete
			0x14: (
				('string', 'text'),
			),
			#Client Settings
			0x15: (
				('string', 'locale'),
				('byte'  , 'view_distance'),
				('byte'  , 'chat_flags'),
				('bool'  , 'unused'),
				('byte'  , 'difficulty'),
				('bool'  , 'show_cape'),
			),
			#Client Status
			0x16: (
				('byte', 'action'),
			),
			#Plugin Message
			0x17: (
				('string', 'channel'),
				#Extension
					#byte string 'data'
			),
		},
	},
}

#Useful for some lookups
hashed_names = {
	(state, direction, packet_id): 
	packet_names[state][direction][packet_id]
	for state in packet_names
	for direction in packet_names[state]
	for packet_id in packet_names[state][direction]
}
hashed_structs = {
	(state, direction, packet_id): 
	packet_structs[state][direction][packet_id]
	for state in packet_structs
	for direction in packet_structs[state]
	for packet_id in packet_structs[state][direction]
}

#Pack the protocol more efficiently
packet_names = tuple(tuple(packet_names[i][j] for j in (0,1)) for i in (0,1,2,3))
packet_structs = tuple(tuple(packet_structs[i][j] for j in (0,1)) for i in (0,1,2,3))