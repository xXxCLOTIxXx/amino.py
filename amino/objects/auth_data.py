from ..helpers.generator import generate_user_agent, generate_deviceId

class auth_data:
	"""
	class with account login data

	attributes:
	
	- sid
	- uid
	- user_agent
	- language
	- deviceId

	"""
	sid: str | None = None
	uid: str | None = None
	_user_agent: str = None
	language: str = None 
	_deviceId: str = None
	auto_device: bool = False
	auto_user_agent: bool = False

	def __init__(self, deviceId: str | None = None, language: str = "en", user_agent: str | None = None, auto_device: bool = False, auto_user_agent: bool = False):
		self._deviceId = deviceId if deviceId else generate_deviceId()
		self.language = language
		self._user_agent = user_agent if user_agent else generate_user_agent()
		self.auto_device = auto_device
		self.auto_user_agent = auto_user_agent
	
	@property
	def deviceId(self):
		return self._deviceId if self.auto_device is False else generate_deviceId()

	@property
	def user_agent(self):
		return self._user_agent if self.auto_user_agent is False else generate_user_agent()

	
