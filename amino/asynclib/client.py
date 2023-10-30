from amino.helpers.requester import AsyncRequester
from amino.helpers.headers import headers, tapjoy, tapjoy_headers
from amino.models.objects import profile
from amino.models import objects
from amino.helpers import exceptions
from amino.helpers.generators import generate_deviceId, sid_to_uid
from .socket import SocketHandler, Callbacks

from aiohttp import ClientSession
from asyncio import get_event_loop
from json import dumps
from time import time as timestamp


class Client(AsyncRequester, SocketHandler, Callbacks):
	profile = profile()

	def __init__(self, deviceId: str = None, auto_device: bool = False, language: str = "en", user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2", socket_enabled: bool = True, socket_debug: bool = False, socket_whitelist_communities: list = None, socket_old_message_mode: bool = False, proxies: dict = None, certificate_path = None):
		AsyncRequester.__init__(self, session=ClientSession(), proxies=proxies, verify=certificate_path)
		if socket_enabled:
			SocketHandler.__init__(self, old_message_mode=socket_old_message_mode, whitelist_communities=socket_whitelist_communities, debug=socket_debug)
			Callbacks.__init__(self)
		self.socket_enabled=socket_enabled
		self.device_id = deviceId if deviceId else generate_deviceId()
		self.auto_device = auto_device
		self.user_agent=user_agent
		self.language=language

	def __del__(self):
		try:
			loop = get_event_loop()
			loop.run_until_complete(self.close_session())
		except RuntimeError:
			loop = new_event_loop()
			loop.run_until_complete(self.close_session())

	async def close_session(self):
		if not self.session.closed: await self.session.close()

	@property
	def deviceId(self) -> str:
		return generate_deviceId() if self.auto_device else self.device_id

	def get_headers(self, deviceId: str = None, data = None, content_type: str = None, sid: str = None, user_agent = None, language: str = None) -> dict:
		return headers(deviceId=deviceId if deviceId else self.deviceId, data=data, content_type=content_type, sid=sid, user_agent=user_agent if user_agent else self.user_agent, language=language if language else self.language)

	def set_device(self, deviceId: str = None, auto_device: bool = None, set_random_device: bool = False, user_agent: str = None) -> str:
		if auto_device is True: self.auto_device = True
		if auto_device is False: self.auto_device = False
		if set_random_device is True:deviceId = generate_deviceId()
		if user_agent: self.user_agent=user_agent
		if deviceId:self.device_id = deviceId
		if deviceId and user_agent:return (deviceId, user_agent)
		if deviceId: return self.deviceId
		if user_agent: return self.user_agent



#ACCOUNT=============================
	async def login(self, email: str, password: str = None, secret: str = None) -> profile:
		deviceId = self.deviceId
		data = dumps({
			"email": email,
			"v": 2,
			"secret": secret if secret else f"0 {password}",
			"deviceID": deviceId,
			"clientType": 100,
			"action": "normal",
			"timestamp": int(timestamp() * 1000)
		})

		response = await self.make_request(method="POST", endpoint="/g/s/auth/login", body=data, headers=self.get_headers(data=data, deviceId=deviceId))
		self.profile = profile(await response.json())
		if self.socket_enabled:await self.connect()
		return self.profile