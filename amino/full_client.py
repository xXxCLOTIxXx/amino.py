from .models.objects import profile
from .client import Client

class FullClient(Client):
	def __init__(self, profile: profile = None, deviceId: str = None, auto_device: bool = False, language: str = "en", user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2", socket_enabled: bool = True, socket_debug: bool = False, socket_trace: bool = False, socket_whitelist_communities: list = None, socket_old_message_mode: bool = False, proxies: dict = None, certificate_path = None):
		Client.__init__(self, language=language, user_agent=user_agent, deviceId=deviceId, auto_device=auto_device, socket_enabled=socket_enabled, socket_debug=socket_debug, socket_trace=socket_trace, socket_whitelist_communities=socket_whitelist_communities, socket_old_message_mode=socket_old_message_mode, proxies=proxies, certificate_path=certificate_path)
		if profile:self.profile=profile