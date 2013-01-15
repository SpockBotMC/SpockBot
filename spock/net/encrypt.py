from spock.mcp import utils
import hashlib

def HashServerId(serverid, sharedsecret, pubkey):
	sha1 = hashlib.sha1()
	sha1.update(serverid)
	sha1.update(sharedsecret)
	sha1.update(pubkey)
	return utils.javaHexDigest(sha1)