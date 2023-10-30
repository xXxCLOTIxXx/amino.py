from .client import Client


class LocalClient(Client):
	def __init__(self):
		Client.__init__(self)