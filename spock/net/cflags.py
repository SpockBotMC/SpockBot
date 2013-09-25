cflags = {
	'SOCKET_ERR':  0x0001, # Socket Error (select.POLLERR set)
	'SOCKET_HUP':  0x0002, # Socket Hung up (select.POLLHUP set)
	'SOCKET_RECV': 0x0004, # Socket is ready to recieve data (select.POLLIN set)
	'SOCKET_SEND': 0x0008, # Socket is ready to send data (select.POLLOUT set) and Send buffer contains data to send
	'LOGIN_ERR':   0x0010, # Error while logging into Minecraft.net
	'AUTH_ERR':    0x0020, # Error authenticating session
	'START_EVENT': 0x0040, # Event loop is going to start
	'KILL_EVENT':  0x0080, # Kill event recieved
	'RBUFF_RECV':  0x0100, # Read buffer has data ready to be unpacked
	'UNDEFINED10': 0x0200,
	'UNDEFINED11': 0x0400,
	'UNDEFINED12': 0x0800,
	'UNDEFINED13': 0x1000,
	'UNDEFINED14': 0x2000,
	'UNDEFINED15': 0x4000,
	'UNDEFINED16': 0x8000,
}

cevents = [
	'start',
	'chat',
	'whisper',
	'message',
	'login',
	'spawn',
	'respawn',
	'game',
	'rain',
	'time',
	'kicked',
	'end',
	'spawn_reset',
	'death',
	'health',
	'entity_swing_arm',
	'entity_hurt',
	'entity_wake',
	'entity_eat',
	'entity_crouch',
	'entity_uncrouch',
	'entity_equipment_change',
	'entity_sleep',
	'entity_spawn',
	'entity_collect',
	'entity_gone',
	'entity_move',
	'entity_detach',
	'entity_attach',
	'entity_update',
	'entity_effect',
	'entity_effect_end',
	'player_joined',
	'player_left',
	'block_update',
	#'block_update_xyz',
	'chunk_column_load',
	'chunk_column_unload',
	'note_heard',
	'piston_move',
	'chest_lid_move',
	'digging_complete',
	'digging_aborted',
	'move',
	'mount',
	'dismount',
	'window_open',
	'window_close',
	'sleep',
	'wake',
	'experience',
]

#2 values = Attribute&Setting name, default value
#3 values = Attribute name, setting name, default value
defstruct = [
	('plugins', []),
	('plugin_settings', {}),
	('mc_username', 'username', 'Bot'),
	('mc_password', 'password', ''),
	('daemon', False),
	('logfile', ''),
	('pidfile', ''),
	('authenticated', True),
	('bufsize', 4096),
	('sock_quit', True),
	('sess_quit', True),
	('proxy', {
		'enabled': False,
		'host': '',
		'port': 0,
	}),
]

for index, setting in enumerate(defstruct):
	if len(setting) == 2:
		defstruct[index] = (setting[0], setting[0], setting[1])