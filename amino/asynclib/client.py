from amino.helpers.requester import AsyncRequester
from amino.helpers.headers import headers, tapjoy, tapjoy_headers
from amino.models.objects import profile
from amino.models import objects
from amino.helpers import exceptions
from amino.helpers.generators import generate_deviceId, sid_to_uid, generate_user_agent
from .socket import SocketHandler, Callbacks

from aiohttp import ClientSession
from asyncio import get_event_loop, create_task, new_event_loop
from json import dumps
from time import time as timestamp


class Client(AsyncRequester, SocketHandler, Callbacks):
	profile = profile()

	def __init__(self, deviceId: str = None, auto_device: bool = False, language: str = "en", user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2", auto_user_agent: bool = False, socket_enabled: bool = True, socket_debug: bool = False, socket_whitelist_communities: list = None, proxies: dict = None, certificate_path = None):
		AsyncRequester.__init__(self, session=ClientSession(), proxies=proxies, verify=certificate_path)
		if socket_enabled:
			SocketHandler.__init__(self, whitelist_communities=socket_whitelist_communities, debug=socket_debug)
			Callbacks.__init__(self)
		self.socket_enabled=socket_enabled
		self.device_id = deviceId if deviceId else generate_deviceId()
		self.auto_device = auto_device
		self.auto_user_agent = auto_user_agent
		self._user_agent=user_agent
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

	@property
	def user_agent(self) -> str:
		return generate_user_agent() if self.auto_user_agent else self._user_agent

	def get_headers(self, deviceId: str = None, data = None, content_type: str = None, sid: str = None, user_agent = None, language: str = None) -> dict:
		return headers(deviceId=deviceId if deviceId else self.deviceId, data=data, content_type=content_type, sid=sid, user_agent=user_agent if user_agent else self.user_agent, language=language if language else self.language)

	def set_device(self, deviceId: str = None, auto_device: bool = None, set_random_device: bool = False, user_agent: str = None, set_random_user_agent: bool = False) -> str:
		if auto_device is True: self.auto_device = True
		if auto_device is False: self.auto_device = False
		if set_random_device is True:deviceId = generate_deviceId()
		if set_random_user_agent is True:deviceId = generate_user_agent()
		if user_agent: self._user_agent=user_agent
		if deviceId:self.device_id = deviceId
		if deviceId and user_agent:return (deviceId, user_agent)
		if deviceId: return self.deviceId
		if user_agent: return self._user_agent



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



#SOCKET=============================


	def online(self, comId: int):
		self.online_list.add(comId)

	def offline(self, comId: int):
		try:self.online_list.remove(comId)
		except KeyError:pass


	async def typing_start(self, chatId: str, comId: int = None):

		data = {
			"actions": ["Typing"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		if comId:data["ndcId"]=comId
		await self.send_action(message_type=304, body=data)



	async def typing_end(self, chatId: str, comId: int = None):

		data = {
			"actions": ["Typing"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		if comId:data["ndcId"]=comId
		await self.send_action(message_type=306, body=data)


	async def recording_start(self, chatId: str, comId: int = None):

		data = {
			"actions": ["Recording"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		if comId:data["ndcId"]=comId
		await self.send_action(message_type=304, body=data)

	async def recording_end(self, chatId: str, comId: int = None):

		data = {
			"actions": ["Recording"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		if comId:data["ndcId"]=comId
		await self.send_action(message_type=306, body=data)


	async def join_live_chat(self, chatId: str, comId: int = None, as_viewer: bool = False):

		data = {
			"threadId": chatId,
			"joinRole": 2 if as_viewer else 1,
		}
		if comId:data["ndcId"]=int(comId)
		await self.send_action(message_type=112, body=data)



	async def start_vc(self, chatId: str, comId: int = None, join_as_viewer: bool = False):
		await self.join_live_chat(chatId=chatId, comId=comId, as_viewer=join_as_viewer)
		data = {
			"threadId": chatId,
			"channelType": 1
		}
		if comId:data["ndcId"]=int(comId)
		await self.send_action(message_type=108, body=data)

		self.active_live_chats.append(chatId)
		create_task(self.vc_loop(comId, chatId, join_as_viewer))

	async def end_vc(self, chatId: str, comId: int = None):
		await self.join_live_chat(chatId=chatId, comId=comId, as_viewer=True)
		self.leave_from_live_chat(chatId)

	def leave_from_live_chat(self, chatId: str):
		if chatId in self.active_live_chats:
			self.active_live_chats.remove(chatId)