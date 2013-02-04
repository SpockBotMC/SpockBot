cflags = {
	'SOCKET_RECV': 0x01, # Socket is ready to recieve data
	'SOCKET_SEND': 0x02, # Socket is ready to send data and Send buffer contains data to send
	'RBUFF_RECV':  0x04, # Read buffer has data ready to be unpacked
	'UNDEFINED':   0x08, 
	'POS_UPDT':    0x10, # Client Position state has updated
	'ENT_UPDT':    0x20, # Entity Position states have updated
	'BLK_UPDT':    0x40, # Blocks have updated (Also set if WLD_UPDT is set)
	'WLD_UPDT':    0x80, # World/Chunks have updated
}