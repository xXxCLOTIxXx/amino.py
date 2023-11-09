from amino.helpers.requester import AsyncRequester
from amino.helpers.headers import headers, tapjoy, tapjoy_headers
from amino.models.objects import AsyncObjectCreator
from amino.helpers import exceptions
from amino.helpers.generators import generate_deviceId, sid_to_uid, generate_user_agent
from .socket import SocketHandler, Callbacks

from aiohttp import ClientSession
from asyncio import get_event_loop, create_task, new_event_loop
from json import dumps
from time import time as timestamp
import urllib3

class Client(AsyncRequester, SocketHandler, Callbacks):
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
		bool *requests_debug* - Track requests (Default: False)
		bool *http_connect* - Work with http connection (Default: False)
	"""

	profile = AsyncObjectCreator()

	def __init__(self,
		deviceId: str = None,
		auto_device: bool = False,
		language: str = "en",
		user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2",
		auto_user_agent: bool = False,
		socket_enabled: bool = True,
		socket_debug: bool = False,
		socket_whitelist_communities: list = None,
		proxies: dict = None,
		certificate_path = None,
		http_connect: bool = True,
		requests_debug: bool = False):
		
		
		
		if http_connect:
			urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
		AsyncRequester.__init__(self, session=ClientSession(), proxies=proxies, verify=certificate_path, http_connect=http_connect, requests_debug=requests_debug)
		if socket_enabled:
			SocketHandler.__init__(self, whitelist_communities=socket_whitelist_communities, debug=socket_debug)
			Callbacks.__init__(self)
		self.socket_enabled=socket_enabled
		self.device_id = deviceId if deviceId else generate_deviceId()
		self.auto_device = auto_device
		self.auto_user_agent = auto_user_agent
		self._user_agent=user_agent
		self.language=language

	def __repr__(self):
		return repr(f"sid={self.profile.sid}, userId={self.profile.userId}, deviceId={self.deviceId}, user_agent={self.user_agent}, language={self.language}")

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
		return headers(deviceId=deviceId if deviceId else self.deviceId, data=data, content_type=content_type, sid=sid or self.profile.sid, user_agent=user_agent if user_agent else self.user_agent, language=language if language else self.language)

	def set_device(self, deviceId: str = None, auto_device: bool = None, set_random_device: bool = False, user_agent: str = None, set_random_user_agent: bool = False) -> str:
		if auto_device is True: self.auto_device = True
		if auto_device is False: self.auto_device = False
		if set_random_device is True:deviceId = generate_deviceId()
		if set_random_user_agent is True:deviceId = generate_user_agent()
		if user_agent: self._user_agent=user_agent
		if deviceId:self.device_id = deviceId
		if deviceId or user_agent:return (deviceId, user_agent)


#ACCOUNT=============================

	async def auth(self, email: str = None, number: str = None, sid: str = None, password: str = None, secret: str = None) -> AsyncObjectCreator:
		
		if sid:
			return await self.login_sid(sid=sid, need_account_info=True)
		if password is None and secret is None: raise exceptions.SpecifyType("Specify password or secret.")
		if email:
			return await self.login(email=email, password=password, secret=secret)
		if number:
			return await self.login_phone(email=email, password=password, secret=secret)
		raise exceptions.SpecifyType("Specify sid or email or number.")


	async def login(self, email: str, password: str = None, secret: str = None) -> AsyncObjectCreator:
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

		response = await self.make_request(method="POST", endpoint="/g/s/auth/login", data=data, headers=self.get_headers(data=data, deviceId=deviceId))
		self.profile = AsyncObjectCreator(await response.json())
		if self.socket_enabled:await self.connect()
		return self.profile

	

	async def login_phone(self, phone: str, password: str = None, secret: str = None) -> AsyncObjectCreator:

		deviceId = self.deviceId
		if password is None and secret is None: raise exceptions.SpecifyType
		data = dumps({
			"phoneNumber": phone,
			"v": 2,
			"secret": secret if secret else f"0 {password}",
			"deviceID": deviceId,
			"clientType": 100,
			"action": "normal",
			"timestamp": int(timestamp() * 1000)
		})

		response = await self.make_request(method="POST", endpoint="/g/s/auth/login", data=data, headers=self.get_headers(data=data, deviceId=deviceId))
		self.profile = AsyncObjectCreator(await response.json())
		if self.socket_enabled:await self.connect()
		return self.profile


	async def login_sid(self, sid: str, need_account_info: bool = False) -> AsyncObjectCreator:
		data = {"sid": sid, "auid": sid_to_uid(sid)}
		if need_account_info:data["userProfile"]=await self.get_user_info(sid_to_uid(sid))
		self.profile=AsyncObjectCreator(data)
		if self.socket_enabled:await self.connect()
		return self.profile




	async def logout(self) -> int:

		deviceId = self.deviceId
		data = dumps({
			"deviceID": deviceId,
			"clientType": 100,
			"timestamp": int(timestamp() * 1000)
		})


		response = await self.make_request(method="POST", endpoint="/g/s/auth/logout", data=data, headers=self.get_headers(data=data, deviceId=deviceId))
		if self.socket_enabled: await self.disconnect()
		self.profile = AsyncObjectCreator()
		return response.status_code


#OBJECTS=============================
	async def get_from_link(self, link: str) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/link-resolution?q={link}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json()["linkInfoV2"])




#SOCKET=============================


	async def create_socket_event(self, data):
		return await self.call(data)

	async def online(self, comId: int):

		data = {
			"actions": ["Browsing"],
			"target":f"ndc://x{comId}/",
			"ndcId":comId
		}
		if data in self.actions_list: return
		self.actions_list.append(data)
		await self.send_action(message_type=304, body=data)

	async def offline(self, comId: int):

		data = {
			"actions": ["Browsing"],
			"target":f"ndc://x{comId}/",
			"ndcId":comId
		}
		if data not in self.actions_list: return
		self.actions_list.remove(data)
		await self.send_action(message_type=306, body=data)


	async def browsing_blogs_start(self, comId: int, blogId: str = None, quizId: str = None):
		data = {
			"actions": ["Browsing"],
			"target": f"ndc://x{comId}/blog/{blogId or quizId}",
			"ndcId":comId,
			"params": {
				"blogType": 0 if blogId else 6,
				}
		}

		if data not in self.actions_list: self.actions_list.append(data)
		await self.send_action(message_type=304, body=data)


	async def browsing_blogs_end(self, comId: int, blogId: str = None, quizId: str = None):
		data = {
			"actions": ["Browsing"],
			"target": f"ndc://x{comId}/blog/{blogId or quizId}",
			"ndcId":comId,
			"params": {
				"blogType": 0 if blogId else 6,
				}
		}

		if data in self.actions_list: self.actions_list.remove(data)
		await self.send_action(message_type=306, body=data)
	



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
	
	async def receive_messages(self):
		if self.socket_enabled and self.connect:await self.receive()