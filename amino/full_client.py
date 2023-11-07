from .client import Client

class FullClient(Client):

	"""
	***server settings***
		str *language* - Language for response from the server (Default: "en")
		str *user_agent* - user agent (Default: "Apple iPhone12,1 iOS v15.5 Main/3.12.2")
		bool *auto_user_agent* - Does each request generate a new user agent? (Default: False)
		str *deviceId* - device id (Default: None)
		bool *auto_device* - Does each request generate a new deviceId? (Default: False)
		str *certificate_path* - path to certificates (Default: None)
		dict *proxies* - proxies (Default: None)

	***socket settings***
		bool *socket_enabled* - Launch socket? (Default: True)
		bool *socket_debug* - Track the stages of a socket's operation? (Default: False)
		bool *socket_trace* - socket trace (Default: False)
		list *socket_whitelist_communities* - By passing a list of communities the socket will respond only to them (Default: None),
		bool *socket_old_message_mode* - The socket first writes all messages in a separate thread, and basically takes them from a list (Default: False)

	"""

	def __init__(self, deviceId: str = None, auto_device: bool = False, language: str = "en", user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2", auto_user_agent: bool = False, socket_enabled: bool = True, socket_debug: bool = False, socket_trace: bool = False, socket_whitelist_communities: list = None, socket_old_message_mode: bool = False, proxies: dict = None, certificate_path = None):
		Client.__init__(self, language=language, user_agent=user_agent, deviceId=deviceId, auto_device=auto_device, auto_user_agent=auto_user_agent, socket_enabled=socket_enabled, socket_debug=socket_debug, socket_trace=socket_trace, socket_whitelist_communities=socket_whitelist_communities, socket_old_message_mode=socket_old_message_mode, proxies=proxies, certificate_path=certificate_path)