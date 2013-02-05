cflags = {
	'SOCKET_RECV': 0x0001, # Socket is ready to recieve data
	'SOCKET_SEND': 0x0002, # Socket is ready to send data and Send buffer contains data to send
	'RBUFF_RECV':  0x0004, # Read buffer has data ready to be unpacked
	'UNDEFINED04': 0x0008, 
	'POS_UPDT':    0x0010, # Client Position state has updated
	'ENT_UPDT':    0x0020, # Entity Position states have updated
	'BLK_UPDT':    0x0040, # Blocks have updated (Also set if WLD_UPDT is set)
	'WLD_UPDT':    0x0080, # World/Chunks have updated
	'UNDEFINED09': 0x0100,
	'UNDEFINED10': 0x0200,
	'UNDEFINED11': 0x0400,
	'UNDEFINED12': 0x0800,
	'UNDEFINED13': 0x1000,
	'UNDEFINED14': 0x2000,
	'UNDEFINED15': 0x4000,
	'UNDEFINED16': 0x8000,
}