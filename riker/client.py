import spock.net.client

class RikerClient(spock.net.client.Client):
    def __init__(self):
        super(RikerClient, self).__init__()