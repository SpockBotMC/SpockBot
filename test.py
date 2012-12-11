import socket


def get_info(host='localhost', port=25565):
    #Set up our socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    
    #Send 0xFE: Server list ping
    s.send('\xFE\x01')
    
    #Read some data
    d = s.recv(1024)
    s.close()
    
    #Check we've got a 0xFF Disconnect
    assert d[0] == '\xff'
    
    #Remove the packet ident (0xFF) and the short containing the length of the string
    #Decode UCS-2 string
    d = d[3:].decode('utf-16be')
    
    #Check the first 3 characters of the string are what we expect
    assert d[:3] == u'\xa7\x31\x00'
    
    #Split
    d = d[3:].split('\x00')
    
    #Return a dict of values
    return {'protocol_version': int(d[0]),
            'server_version': d[1],
            'motd': d[2],
            'players': int(d[3]),
            'max_players': int(d[4])}

print get_info(host='untamedears.com')