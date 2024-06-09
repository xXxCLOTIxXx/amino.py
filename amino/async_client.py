from .objects.auth_data import auth_data
from .helpers.requests_builder import AsyncRequestsBuilder
from .helpers.generator import generate_deviceId, sid_to_uid
from .helpers.exceptions import SpecifyType
from .ws.AsyncSocket import AsyncSocket
from .objects.reqObjects import DynamicObject


from time import time as timestamp


class AsyncClient(AsyncSocket):
	req: AsyncRequestsBuilder
	socket_enable = True

	def __init__(self, deviceId: str = None, language: str = "en", user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2", proxies: dict = None, socket_enable: bool = True, sock_debug: bool = False):
		self.req = AsyncRequestsBuilder(
			proxies=proxies,
			profile=auth_data(
				deviceId=deviceId if deviceId else generate_deviceId(),
				language=language,
				user_agent=user_agent
			)
		)
		self.socket_enable = socket_enable
		AsyncSocket.__init__(self, sock_debug)

	
	@property
	def profile(self):
		return self.req.profile
	
	@property
	def userId(self):
		return self.req.profile.uid

	@property
	def sid(self):
		return self.req.profile.sid

	@property
	def deviceId(self):
		return self.req.profile.deviceId



	async  def login(self, email: str, password: str = None, secret: str = None) -> DynamicObject:
		if password is None and secret is None: raise SpecifyType
		result = await self.req.request("POST", "/g/s/auth/login", {
			"email": email,
			"v": 2,
			"secret": secret if secret else f"0 {password}",
			"deviceID": self.deviceId,
			"clientType": 100,
			"action": "normal",
		})
		self.req.profile.sid, self.req.profile.uid = result["sid"], result["auid"]
		if self.socket_enable:
			final = f"{self.deviceId}|{int(timestamp() * 1000)}"
			await self.ws_connect(final=final, headers=self.ws_headers(self.sid, final, self.deviceId))
		return result["userProfile"]


	async def login_phone(self, phone: str, password: str = None, secret: str = None) -> DynamicObject:
		if password is None and secret is None: raise SpecifyType
		result = await self.req.request("POST", "/g/s/auth/login", {
			"phoneNumber": phone,
			"v": 2,
			"secret": secret if secret else f"0 {password}",
			"deviceID": self.deviceId,
			"clientType": 100,
			"action": "normal",
		})
		self.req.profile.sid, self.req.profile.uid = result["sid"], result["auid"]
		if self.socket_enable:
			final = f"{self.deviceId}|{int(timestamp() * 1000)}"
			await self.ws_connect(final=final, headers=self.ws_headers(self.sid, final, self.deviceId))
		return result["userProfile"]

	
	async def login_sid(self, sid: str) -> auth_data:
		self.req.profile.sid, self.req.profile.uid = sid, sid_to_uid(sid)
		if self.socket_enable:
			final = f"{self.deviceId}|{int(timestamp() * 1000)}"
			await self.ws_connect(final=final, headers=self.ws_headers(self.sid, final, self.deviceId))
		return self.profile



	async def logout(self) -> DynamicObject:
		result = await self.req.request("POST", "/g/s/auth/logout", {
			"deviceID": self.profile.deviceId,
			"clientType": 100,
		})
		self.req.profile.sid, self.req.profile.uid = None, None
		if self.socket_enable:await self.ws_disconnect()
		return result