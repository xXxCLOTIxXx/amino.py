from .socket import SocketHandler, Callbacks
from .helpers.requester import Requester
from .helpers.headers import headers
from .helpers.objects import profile
from .helpers import objects
from .helpers.generators import generate_deviceId, sid_to_uid

from requests import Session
from time import time as timestamp
from json import loads, dumps

class Client(SocketHandler, Requester, Callbacks):
	profile = profile()

	def __init__(self, user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2", deviceId: str = None, auto_device: bool = False, socket_enabled: bool = True, socket_debug: bool = False, socket_trace: bool = False, socket_whitelist_communities: list = None, socket_old_message_mode: bool = False, proxies: dict = None, certificate_path = None):
		Requester.__init__(self, session=Session(), proxies=proxies, verify=certificate_path)
		self.socket_enabled=socket_enabled
		if socket_enabled:
			SocketHandler.__init__(self, old_message_mode=socket_old_message_mode, whitelist_communities=socket_whitelist_communities, sock_trace=socket_trace, debug=socket_debug)
			Callbacks.__init__(self)
		self.device_id = deviceId if deviceId else generate_deviceId()
		self.auto_device = auto_device
		self.user_agent=user_agent


	@property
	def deviceId(self):
		return generate_deviceId() if self.auto_device else self.device_id

	def login(self, email: str, password: str = None, secret: str = None):
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

		response = self.make_request(method="POST", endpoint="/g/s/auth/login", body=data, headers=headers(data=data, deviceId=deviceId, user_agent=self.user_agent)).json()
		self.profile = profile(response)
		if self.socket_enabled:self.connect()
		return self.profile


	def login_phone(self, phone: str, password: str):

		deviceId = self.deviceId
		data = dumps({
			"phoneNumber": phone,
			"v": 2,
			"secret": f"0 {password}",
			"deviceID": deviceId,
			"clientType": 100,
			"action": "normal",
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint="/g/s/auth/login", body=data, headers=headers(data=data, deviceId=deviceId, user_agent=self.user_agent)).json()
		self.profile = profile(response)
		if self.socket_enabled:self.connect()
		return self.profile


	def login_sid(self, sid: str, need_account_info: bool = False):
		if need_account_info:
			self.profile=profile({"sid": sid, "auid": sid_to_uid(sid), "userProfile":self.get_user_info(sid_to_uid(sid))})
		else:
			self.profile=profile({"sid": sid, "auid": sid_to_uid(sid)})
		if self.socket_enabled:self.connect()
		return self.profile

	def get_from_link(self, link: str):

		response = self.make_request(method="GET", endpoint=f"/g/s/link-resolution?q={link}", headers=headers(deviceId=self.deviceId, user_agent=self.user_agent)).json()
		return objects.FromCode(response["linkInfoV2"])


	def get_user_info(self, userId: str):

		response = self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}", headers=headers(deviceId=self.deviceId, user_agent=self.user_agent)).json()
		return objects.UserProfile(response["userProfile"])