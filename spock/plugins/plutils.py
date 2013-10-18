def pl_announce(*args):
	def inner(cl):
		cl.pl_announce = args
		return cl
	return inner