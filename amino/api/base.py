from amino.helpers.requester import Requester
from amino import update_deviceId
from amino import AuthData


class BaseClass():
	req: Requester
	socket_enable: bool
	account: AuthData = AuthData({})
	
	@property
	def deviceId(self) -> str:
		return self.req.deviceId

	@property
	def userId(self) -> str | None:
		return self.req.userId

	@property
	def sid(self) -> str | None:
		return self.req.sid

	@property
	def user_agent(self) -> str:
		return self.req.user_agent

	@property
	def language(self) -> str:
		return self.req.language


	def set_device(self, deviceId: str) -> None:
		self.req.deviceId = deviceId
	
	def update_device(self) -> None:
		if self.req.deviceId: self.req.deviceId = update_deviceId(self.req.deviceId)
	
	def set_language(self, language: str) -> None:
		self.req.language = language
	
	def set_user_agent(self, user_agent: str) -> None:
		self.req.user_agent = user_agent
	
	def set_userId(self, userId: str | None) -> None:
		self.req.userId = userId

	def set_sid(self, sid: str | None) -> None:
		self.req.sid = sid