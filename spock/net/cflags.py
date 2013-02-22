cflags = {
	'SOCKET_ERR':  0x0001, # Socket Error (select.POLLERR set)
	'SOCKET_HUP':  0x0002, # Socket Hung up (select.POLLHUP set)
	'SOCKET_RECV': 0x0004, # Socket is ready to recieve data (select.POLLIN set)
	'SOCKET_SEND': 0x0008, # Socket is ready to send data (select.POLLOUT set) and Send buffer contains data to send
	'LOGIN_ERR':   0x0010, # Error while logging into Minecraft.net
	'AUTH_ERR':    0x0020, # Error authenticating session
	'KILL_EVENT':  0x0040, # Kill event recieved
	'UNDEFINED08': 0x0080,
	'RBUFF_RECV':  0x0100, # Read buffer has data ready to be unpacked
	'UNDEFINED10': 0x0200,
	'UNDEFINED11': 0x0400,
	'UNDEFINED12': 0x0800,
	'UNDEFINED13': 0x1000,
	'UNDEFINED14': 0x2000,
	'UNDEFINED15': 0x4000,
	'UNDEFINED16': 0x8000,
}