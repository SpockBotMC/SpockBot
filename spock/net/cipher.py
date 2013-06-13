from Crypto.Cipher import AES

class AESCipher():
	def __init__(self, SharedSecret):
		self.encipher = AES.new(SharedSecret, AES.MODE_CFB, IV=SharedSecret)
		self.decipher = AES.new(SharedSecret, AES.MODE_CFB, IV=SharedSecret)

	def encrypt(self, data):
		return self.encipher.encrypt(data)

	def decrypt(self, data):
		return self.decipher.decrypt(data)