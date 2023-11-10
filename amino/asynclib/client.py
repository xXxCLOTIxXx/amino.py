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
from uuid import UUID
from os import urandom
from typing import Union
from binascii import hexlify
from base64 import b64encode
from aiofiles.threadpool.binary import AsyncBufferedReader
from locale import getdefaultlocale as locale
from time import timezone as tz
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
		if need_account_info:
			up = await self.get_user_info(sid_to_uid(sid))
			data["userProfile"]=up.userProfile
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
		return response.status

	async def register_account(self, nickname: str, email: str, password: str, verificationCode: str, deviceId: str = None, timeout: int = None) -> AsyncObjectCreator:

		if deviceId is None:
			deviceId = self.deviceId
		data = dumps({
			"secret": f"0 {password}",
			"deviceID": deviceId,
			"email": email,
			"clientType": 100,
			"nickname": nickname,
			"latitude": 0,
			"longitude": 0,
			"address": None,
			"clientCallbackURL": "narviiapp://relogin",
			"validationContext": {
				"data": {
					"code": verificationCode
				},
				"type": 1,
				"identity": email
			},
			"type": 1,
			"identity": email,
			"timestamp": int(timestamp() * 1000)
		}) 
		response = await self.make_request(method="POST", endpoint="/g/s/auth/register", data=data, headers=self.get_headers(data=data, deviceId=deviceId), timeout=timeout)
		return AsyncObjectCreator(await response.json())



	async def restore_account(self, email: str, password: str) -> int:

		deviceId = self.deviceId
		data = dumps({
			"secret": f"0 {password}",
			"deviceID": deviceId,
			"email": email,
			"timestamp": int(timestamp() * 1000)
		})

		response = await self.make_request(method="POST", endpoint="/g/s/account/delete-request/cancel", data=data, headers=self.get_headers(data=data, deviceId=deviceId))
		return response.status



	async def logout(self) -> int:

		deviceId = self.deviceId
		data = dumps({
			"deviceID": deviceId,
			"clientType": 100,
			"timestamp": int(timestamp() * 1000)
		})

		response = await self.make_request(method="POST", endpoint="/g/s/auth/logout", data=data, headers=self.get_headers(data=data, deviceId=deviceId))
		self.profile = AsyncObjectCreator()
		if self.socket_enabled:self.close()
		return response.status

	async def configure_account(self, age: int, gender: str) -> int:

		if age <= 12: raise exceptions.AgeTooLow()
		if gender.lower() == "male": gender = 1
		elif gender.lower() == "female": gender = 2
		elif gender.lower() == "non-binary": gender = 255
		else: raise exceptions.SpecifyType()

		data = dumps({
			"age": age,
			"gender": gender,
			"timestamp": int(timestamp() * 1000)
		})

		response = await self.make_request(method="POST", endpoint="/g/s/persona/profile/basic", data=data, headers=self.get_headers(data=data))
		return response.status

	async def set_amino_id(self, aminoId: str) -> int:

		data = dumps({
			"aminoId": aminoId,
			"timestamp": int(timestamp() * 1000)
			})

		response = await self.make_request(method="POST", endpoint="/g/s/account/change-amino-id", data=data, headers=self.get_headers(data=data))
		return response.status


	async def set_privacy_status(self, isAnonymous: bool = False, getNotifications: bool = False) -> int:

		data = {
			"timestamp": int(timestamp() * 1000),
			"privacyMode": 2 if isAnonymous else 1
			}
		if not getNotifications: data["notificationStatus"] = 2
		else: data["privacyMode"] = 1

		data = dumps(data)
		response = await self.make_request(method="POST", endpoint="/g/s/account/visit-settings", data=data, headers=self.get_headers(data=data))
		return response.status




	async def verify_email(self, email: str, code: str) -> int:

		deviceId = self.deviceId
		data = dumps({
			"validationContext": {
				"type": 1,
				"identity": email,
				"data": {"code": code}},
			"deviceID": deviceId,
			"timestamp": int(timestamp() * 1000)
		})

		response = await self.make_request(method="POST", endpoint="/g/s/auth/check-security-validation", data=data, headers=self.get_headers(data=data, deviceId=deviceId))
		return response.status



	async def request_verify_code(self, email: str, resetPassword: bool = False, timeout: int = None) -> int:

		deviceId = self.deviceId
		data = {
			"identity": email,
			"type": 1,
			"deviceID": deviceId
		}
		if resetPassword:
			data["level"] = 2
			data["purpose"] = "reset-password"
		data = dumps(data)

		response = await self.make_request(method="POST", endpoint="/g/s/auth/request-security-validation", data=data, headers=self.get_headers(data=data, deviceId=deviceId), timeout=timeout)
		return response.status


	async def activate_account(self, email: str, code: str) -> int:

		deviceId = self.deviceId
		data = dumps({
			"type": 1,
			"identity": email,
			"data": {"code": code},
			"deviceID": deviceId
		})

		response = await self.make_request(method="POST", endpoint="/g/s/auth/activate-email", data=data, headers=self.get_headers(data=data, deviceId=deviceId))
		return response.status




	async def delete_account(self, password: str) -> int:

		deviceId = self.deviceId
		data = dumps({
			"deviceID":deviceId,
			"secret": f"0 {password}"
		})

		response = await self.make_request(method="POST", endpoint="/g/s/account/delete-request", data=data, headers=self.get_headers(data=data, deviceId=deviceId))
		return response.status


	async def change_password(self, email: str, password: str, code: str) -> int:

		deviceId = self.deviceId
		data = dumps({
			"updateSecret": f"0 {password}",
			"emailValidationContext": {
				"data": {
					"code": code
				},
				"type": 1,
				"identity": email,
				"level": 2,
				"deviceID": deviceId
			},
			"phoneNumberValidationContext": None,
			"deviceID": deviceId
		})

		response = await self.make_request(method="POST", endpoint="/g/s/auth/reset-password", data=data, headers=self.get_headers(data=data, deviceId=deviceId))
		return response.status


	async def check_deviceId(self, deviceId: str) -> tuple:

		data = dumps({
			"deviceID": deviceId,
			"bundleID": "com.narvii.amino.master",
			"clientType": 100,
			"timezone": -tz // 1000,
			"systemPushEnabled": True,
			"locale": locale()[0],
			"timestamp": int(timestamp() * 1000)
		})

		response = await self.make_request(method="POST", endpoint="/g/s/device", data=data, headers=self.get_headers(data=data, deviceId=deviceId), successfully=None)
		try:response_data = AsyncObjectCreator(await response.json())
		except:response_data = response.text
		return (response.status, response_data)


	async def edit_profile(self, nickname: str = None, content: str = None, icon: AsyncBufferedReader = None, backgroundColor: str = None, backgroundImage: str = None, defaultBubbleId: str = None) -> int:

		data = {
			"address": None,
			"latitude": 0,
			"longitude": 0,
			"mediaList": None,
			"eventSource": "UserProfileView",
			"timestamp": int(timestamp() * 1000)
		}

		if nickname: data["nickname"] = nickname
		if icon: data["icon"] = await self.upload_media(icon, "image")
		if content: data["content"] = content
		if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if backgroundImage: data["extensions"] = {"style": {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}}
		if defaultBubbleId: data["extensions"] = {"defaultBubbleId": defaultBubbleId}

		data = dumps(data)
		response = await self.make_request(method="POST", endpoint=f"/g/s/user-profile/{self.profile.userId}", data=data, headers=self.get_headers(data=data))
		return response.status

	async def get_eventlog(self) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/eventlog/profile?language={self.language}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def get_account_info(self) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint="/g/s/account", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())




#WALLET/COINS=============================
	async def get_membership_info(self) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint="/g/s/membership?force=true", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def get_wallet_info(self) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint="/g/s/wallet", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def get_wallet_history(self, start: int = 0, size: int = 25) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/wallet/coin/history?start={start}&size={size}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())

	async def wallet_config(self, level: int) -> int:


		data = dumps({
			"adsLevel": level,
			"timestamp": int(timestamp() * 1000)
		})

		response = await self.make_request(method="POST", endpoint=f"/g/s/wallet/ads/config", data=data, headers=self.get_headers(data=data))
		return response.status

	async def buy_in_store(self, objectId: str, isAutoRenew: bool = False) -> int:
		data = dumps({
			"objectId": objectId,
			"objectType": 114,
			"v": 1,
			"paymentContext":
			{
				"discountStatus": 0,
				"isAutoRenew": isAutoRenew
			},
			"timestamp": timestamp()
		})

		response = await self.make_request(method="POST", endpoint=f"/g/s/store/purchase", data=data, headers=self.get_headers(data=data))
		return response.status

	async def purchase(self, objectId: str, isAutoRenew: bool = False) -> int:
		return await self.buy_in_store(objectId=objectId, isAutoRenew=isAutoRenew)


	async def send_coins(self, coins: int, blogId: str = None, chatId: str = None, objectId: str = None, transactionId: str = None) -> int:

		if transactionId is None: transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))
		data = {
			"coins": coins,
			"tippingContext": {"transactionId": transactionId},
			"timestamp": int(timestamp() * 1000)
		}

		if blogId is not None: url = f"/g/s/blog/{blogId}/tipping"
		elif chatId is not None: url = f"/g/s/chat/thread/{chatId}/tipping"
		elif objectId is not None:
			data["objectId"] = objectId
			data["objectType"] = 2
			url = f"/g/s/tipping"
		else: raise exceptions.SpecifyType()

		data = dumps(data)
		response = await self.make_request(method="POST", endpoint=url, data=data, headers=self.get_headers(data=data))
		return response.status

	async def claim_new_user_coupon(self) -> int:

		response = await self.make_request(method="POST", endpoint="/g/s/coupon/new-user-coupon/claim", headers=self.get_headers())
		return response.status


	async def get_subscriptions(self, start: int = 0, size: int = 25) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/store/subscription?objectType=122&start={start}&size={size}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())



#OBJECTS=============================
	async def get_from_link(self, link: str) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/link-resolution?q={link}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())
	
	async def link_identify(self, link: str) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/community/link-identify?q=http%3A%2F%2Faminoapps.com%2Finvite%2F{link}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())

	async def get_from_deviceId(self, deviceId: str) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/auid?deviceId={deviceId}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def get_from_Id(self, objectId: str, objectType: int, comId: str = None) -> AsyncObjectCreator:

		data = dumps({
			"objectId": objectId,
			"targetCode": 1,
			"objectType": objectType,
			"timestamp": int(timestamp() * 1000)
		})

		response = await self.make_request(method="GET", endpoint=f"/g/{f's-x{comId}' if comId else 's'}/link-resolution", data=data, headers=self.get_headers(data=data))
		return AsyncObjectCreator(await response.json())




#USERS=============================
	async def get_user_info(self, userId: str) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())

	async def get_all_users(self, start: int = 0, size: int = 25) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/user-profile?type=recent&start={start}&size={size}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def get_user_following(self, userId: str, start: int = 0, size: int = 25) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/joined?start={start}&size={size}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())

	async def get_user_followers(self, userId: str, start: int = 0, size: int = 25) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/member?start={start}&size={size}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())

	async def get_user_visitors(self, userId: str, start: int = 0, size: int = 25) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/visitors?start={start}&size={size}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def get_blocked_users(self, start: int = 0, size: int = 25) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/block?start={start}&size={size}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def get_blocker_users(self, start: int = 0, size: int = 25) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/block/full-list?start={start}&size={size}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def get_wall_comments(self, userId: str, sorting: str, start: int = 0, size: int = 25) -> AsyncObjectCreator:

		if sorting.lower() not in ("newest", "oldest", "vote"): raise exceptions.WrongType(sorting)
		response = await self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/g-comment?sort={sorting}&start={start}&size={size}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())

	async def visit(self, userId: str) -> int:

		response = await self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}?action=visit", headers=self.get_headers())
		return response.status

	async def follow(self, userId: Union[str, list]) -> int:

		if isinstance(userId, str):
			response = await self.make_request(method="POST", endpoint=f"/g/s/user-profile/{userId}/member", headers=self.get_headers())
		elif isinstance(userId, list):
			data = dumps({"targetUidList": userId, "timestamp": int(timestamp() * 1000)})
			response = await self.make_request(method="POST", endpoint=f"/g/s/user-profile/{self.profile.userId}/joined", data=data, headers=self.get_headers(data=data))
		else: raise exceptions.WrongType(userId)
		return response.status


	async def unfollow(self, userId: str) -> int:

		response = await self.make_request(method="DELETE", endpoint=f"/g/s/user-profile/{userId}/member/{self.profile.userId}", headers=self.get_headers())
		return response.status


	async def block(self, userId: str) -> int:

		response = await self.make_request(method="POST", endpoint=f"/g/s/block/{userId}", headers=self.get_headers())
		return response.status

	async def unblock(self, userId: str) -> int:

		response = await self.make_request(method="DELETE", endpoint=f"/g/s/block/{userId}", headers=self.get_headers())
		return response.status




#COMMYNITY=============================
	async def get_my_communites(self, start: int = 0, size: int = 25) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/community/joined?v=1&start={start}&size={size}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def my_managed_communities(self, start: int = 0, size: int = 25) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/community/managed?start={start}&size={size}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def get_public_communities(self, language: str = None, size: int = 25) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/topic/0/feed/community?language={language if language else self.language}&type=web-explore&categoryKey=recommendation&size={size}&pagingType=t", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def get_community_info(self, comId: str) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s-x{comId}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount", headers=self.get_headers()).json()
		return AsyncObjectCreator(await response.json())


	async def search_community(self, aminoId: str) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/search/amino-id-and-link?q={aminoId}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())

	async def join_community(self, comId: str, invitationId: str = None) -> int:

		data = {"timestamp": int(timestamp() * 1000)}
		if invitationId: data["invitationId"] = invitationId
		data = dumps(data)

		response = await self.make_request(method="POST", endpoint=f"/x{comId}/s/community/join", data=data, headers=self.get_headers(data=data))
		return response.status


	async def request_join_community(self, comId: str, message: str = None) -> int:

		data = dumps({
			"message": message,
			"timestamp": int(timestamp() * 1000)
			})

		response = await self.make_request(method="POST", endpoint=f"/x{comId}/s/community/membership-request", data=data, headers=self.get_headers(data=data))
		return response.status

	async def leave_community(self, comId: str) -> int:

		response = await self.make_request(method="POST", endpoint=f"/x{comId}/s/community/leave", headers=self.get_headers())
		return response.status



	async def flag_community(self, comId: str, reason: str, flagType: int, isGuest: bool = False) -> int:
		return await self.flag(reason=reason, flagType=flagType, isGuest=isGuest, comId=comId)


	async def reorder_linked_communities(self, comIds: list) -> int:

		data = dumps({
			"ndcIds": comIds,
			"timestamp": int(timestamp() * 1000)
			})

		response = await self.make_request(method="POST", endpoint=f"/g/s/user-profile/{self.profile.userId}/linked-community/reorder", data=data, headers=self.get_headers(data=data))
		return response.status


	async def add_linked_community(self, comId: str) -> int:

		response = await self.make_request(method="POST", endpoint=f"/g/s/user-profile/{self.profile.userId}/linked-community/{comId}", headers=self.get_headers())
		return response.status


	async def remove_linked_community(self, comId: str) -> int:

		response = await self.make_request(method="DELETE", endpoint=f"/g/s/user-profile/{self.profile.userId}/linked-community/{comId}", headers=self.get_headers())
		return response.status


	async def get_linked_communities(self, userId: str) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/linked-community", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())



	async def get_unlinked_communities(self, userId: str) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/linked-community", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())



#CHAT=============================
	async def start_chat(self, userId: Union[str, list], message: str, title: str = None, content: str = None, isGlobal: bool = False, publishToGlobal: bool = False) -> AsyncObjectCreator:

		if isinstance(userId, str): userIds = [userId]
		elif isinstance(userId, list): userIds = userId
		else: raise exceptions.WrongType(type(userId))

		data = {
			"title": title,
			"inviteeUids": userIds,
			"initialMessageContent": message,
			"content": content,
			"timestamp": int(timestamp() * 1000)
		}

		if isGlobal is True: data["type"] = 2; data["eventSource"] = "GlobalComposeMenu"
		else: data["type"] = 0
		if publishToGlobal is True: data["publishToGlobal"] = 1
		else: data["publishToGlobal"] = 0

		data = dumps(data)
		response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread", data=data, headers=self.get_headers(data=data))
		return AsyncObjectCreator(await response.json())


	async def do_not_disturb_chat(self, chatId: str, doNotDisturb: bool = True) -> int:
		data = dumps({"alertOption": 2 if doNotDisturb else 1, "timestamp": int(timestamp() * 1000)})
		response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/member/{self.userId}/alert", data=data, headers=self.get_headers(data=data))
		return response.status

	async def pin_chat(self, chatId: str, pin: bool = True) -> int:
		response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/{'pin' if pin else 'unpin'}", headers=self.get_headers())
		return response.status

	async def add_co_host(self, chatId: str, userIds: list) -> int:
			
		data = dumps({"uidList": userIds, "timestamp": int(timestamp() * 1000)})
		response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/co-host", data=data, headers=self.get_headers(data=data))
		return response.status

	async def edit_chat(self, chatId: str, title: str = None, icon: str = None, backgroundImage: str = None, content: str = None, announcement: str = None, keywords: list = None, pinAnnouncement: bool = None, publishToGlobal: bool = None, canTip: bool = None, viewOnly: bool = None, canInvite: bool = None, fansOnly: bool = None) -> list:

		_data = {"timestamp": int(timestamp() * 1000), "publishToGlobal": 0 if publishToGlobal else 1}

		if title: data["title"] = title
		if content: data["content"] = content
		if icon: data["icon"] = icon
		if keywords: data["keywords"] = keywords
		if announcement: data["extensions"] = {"announcement": announcement}
		if pinAnnouncement: data["extensions"] = {"pinAnnouncement": pinAnnouncement}
		if fansOnly: data["extensions"] = {"fansOnly": fansOnly}

		responses = list()
		if backgroundImage is not None:
			data = dumps({"media": [100, backgroundImage, None], "timestamp": int(timestamp() * 1000)})
			response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/member/{self.userId}/background", data=data, headers=self.get_headers(data=data))
			responses.append({"backgroundImage":response.status if response.status!=200 else exceptions.check_exceptions(await response.json())})
		if viewOnly is not None:
			response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/{'enable' if viewOnly else 'disable'}", headers=self.get_headers(content_type="application/x-www-form-urlencoded"))
			responses.append({"viewOnly":response.status if response.status!=200 else exceptions.check_exceptions(await response.json())})
		if canInvite is not None:
			response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/{'enable' if canInvite else 'disable'}", headers=self.get_headers())
			responses.append({"canInvite":response.status if response.status!=200 else exceptions.check_exceptions(await response.json())})
		if canTip is not None:
			response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/{'enable' if canTip else 'disable'}", headers=self.get_headers())
			responses.append({"canTip":response.status if response.status!=200 else exceptions.check_exceptions(await response.json())})
		data = dumps(_data)

		response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}", data=data, headers=self.get_headers(data=data))
		responses.append({"main":response.status if response.status!=200 else exceptions.check_exceptions(await response.json())})
		return responses




	async def get_my_chats(self, start: int = 0, size: int = 25) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/chat/thread?type=joined-me&start={start}&size={size}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def get_chat_thread(self, chatId: str) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/chat/thread/{chatId}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def get_chat_users(self, chatId: str, start: int = 0, size: int = 25) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())

	async def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str = None) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}"+ f"&pageToken={pageToken}" if pageToken else '', headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def get_message_info(self, chatId: str, messageId: str) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/chat/thread/{chatId}/message/{messageId}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def join_chat(self, chatId: str) -> int:

		response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/member/{self.profile.userId}", headers=self.get_headers(content_type="application/x-www-form-urlencoded"))
		return response.status

	async def leave_chat(self, chatId: str) -> int:

		response = await self.make_request(method="DELETE", endpoint=f"/g/s/chat/thread/{chatId}/member/{self.profile.userId}", headers=self.get_headers())
		return response.status

	async def invite_to_chat(self, userId: Union[str, list], chatId: str) -> int:

		if isinstance(userId, str): userIds = [userId]
		elif isinstance(userId, list): userIds = userId
		else: raise exceptions.WrongType()

		data = dumps({
			"uids": userIds,
			"timestamp": int(timestamp() * 1000)
		})

		response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/member/invite", data=data, headers=self.get_headers(data=data))
		return response.status

	async def kick(self, userId: str, chatId: str, allowRejoin: bool = True) -> int:

		response = await self.make_request(method="DELETE", endpoint=f"/g/s/chat/thread/{chatId}/member/{userId}?allowRejoin={1 if allowRejoin else 0}", headers=self.get_headers())
		return response.status

	async def transfer_host(self, chatId: str, userIds: list) -> int:
		data = dumps({
			"uidList": userIds,
			"timestamp": int(timestamp() * 1000)
		})


		response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/transfer-organizer", data=data, headers=self.get_headers(data=data))
		return response.status

	async def accept_host(self, chatId: str, requestId: str) -> int:

		response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept", data=dumps({}), headers=self.get_headers(data=dumps({})))
		return response.status


	async def delete_co_host(self, chatId: str, userId: str) -> int:

		response = await self.make_request(method="DELETE", endpoint=f"/g/s/chat/thread/{chatId}/co-host/{userId}", headers=self.get_headers())
		return response.status


	async def invite_to_vc(self, chatId: str, userId: str) -> int:

		data = dumps({
			"uid": userId
		})

		response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/vvchat-presenter/invite", data=data, headers=self.get_headers(data=data))
		return response.status


	async def mark_as_read(self, chatId: str, messageId: str) ->  int:

		data = dumps({
			"messageId": messageId,
			"timestamp": int(timestamp() * 1000)
		})

		response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/mark-as-read", data=data, headers=self.get_headers(data=data))
		return response.status


	async def send_message(self, chatId: str, message: str = None, messageType: int = 0, file: AsyncBufferedReader = None, fileType: str = None, replyTo: str = None, mentionUserIds: list = None, stickerId: str = None, embedId: str = None, embedType: int = None, embedLink: str = None, embedTitle: str = None, embedContent: str = None, embedImage: AsyncBufferedReader = None) -> int:

		if message is not None and file is None and mentionUserIds is not None:
			message = message.replace("<@", "‎‏").replace("@>", "‬‭")

		mentions = []
		if mentionUserIds:
			for mention_uid in mentionUserIds:
				mentions.append({"uid": mention_uid})

		if embedImage:
			embedImage = [[100, await self.upload_media(embedImage, "image"), None]]

		data = {
			"type": messageType,
			"content": message,
			"clientRefId": int(timestamp() / 10 % 1000000000),
			"attachedObject": {
				"objectId": embedId,
				"objectType": embedType,
				"link": embedLink,
				"title": embedTitle,
				"content": embedContent,
				"mediaList": embedImage
			},
			"extensions": {"mentionedArray": mentions},
			"timestamp": int(timestamp() * 1000)
		}

		if replyTo: data["replyMessageId"] = replyTo

		if stickerId:
			data["content"] = None
			data["stickerId"] = stickerId
			data["type"] = 3

		if file:
			data["content"] = None
			if fileType == "audio":
				data["type"] = 2
				data["mediaType"] = 110

			elif fileType == "image":
				data["mediaType"] = 100
				data["mediaUploadValueContentType"] = "image/jpg"
				data["mediaUhqEnabled"] = True

			elif fileType == "gif":
				data["mediaType"] = 100
				data["mediaUploadValueContentType"] = "image/gif"
				data["mediaUhqEnabled"] = True

			else: raise exceptions.SpecifyType

			data["mediaUploadValue"] = b64encode(await file.read()).decode()

		data = dumps(data)
		response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/message", data=data, headers=self.get_headers(data=data))
		return response.status

	async def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str = None) -> int:

		data = {
			"adminOpName": 102,
			"timestamp": int(timestamp() * 1000)
		}
		if asStaff and reason:data["adminOpNote"] = {"content": reason}
		data = dumps(data)

		if not asStaff:response = await self.make_request(method="DELETE", endpoint=f"/g/s/chat/thread/{chatId}/message/{messageId}", headers=self.get_headers())
		else:response = await self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/message/{messageId}/admin", data=data, headers=self.get_headers(data=data))
		return response.status




#BLOGS AND ECT=============================
	async def flag(self, reason: str, flagType: int, userId: str = None, blogId: str = None, wikiId: str = None, comId: str = None, asGuest: bool = False) -> int:

		data = {
			"flagType": flagType,
			"message": reason,
			"timestamp": int(timestamp() * 1000)
		}
		if userId:
			data["objectId"] = userId
			data["objectType"] = 0
		elif blogId:
			data["objectId"] = blogId
			data["objectType"] = 1
		elif wikiId:
			data["objectId"] = wikiId
			data["objectType"] = 2
		elif comId:
			data["objectId"] = comId
			data["objectType"] = 16
		else: raise exceptions.SpecifyType

		data = dumps(data)
		response = await self.make_request(method="POST", endpoint=f"/g/s/{'g-flag' if asGuest else 'flag'}", data=data, headers=self.get_headers(data=data))
		return response.status


	async def get_blog_info(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None) -> AsyncObjectCreator:


		if fileId:part=f"shared-folder/files/{fileId}"
		elif blogId or quizId:part=f"blog/{blogId}"
		elif wikiId:part=f"item/{wikiId}"
		else: raise exceptions.SpecifyType

		response = await self.make_request(method="GET", endpoint=f"/g/s/{part}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def get_blog_comments(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, sorting: str = "newest", start: int = 0, size: int = 25) -> AsyncObjectCreator:

		if sorting.lower() not in ("newest", "oldest", "vote"): raise exceptions.WrongType(sorting)
		if fileId:part=f"shared-folder/files/{fileId}"
		elif blogId or quizId:part=f"blog/{blogId}"
		elif wikiId:part=f"item/{wikiId}"
		else: raise exceptions.SpecifyType

		response = await self.make_request(method="GET", endpoint=f"/g/s/{part}/comment?sort={sorting}&start={start}&size={size}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())



	async def comment(self, message: str, userId: str = None, blogId: str = None, wikiId: str = None, replyTo: str = None) -> int:

		data = {
			"content": message,
			"stickerId": None,
			"type": 0,
			"timestamp": int(timestamp() * 1000)
		}
		if replyTo: data["respondTo"] = replyTo
		if userId:
			data["eventSource"] = "UserProfileView"
			part=f"user-profile/{userId}"
		elif blogId:
			data["eventSource"] = "PostDetailView"
			part=f"blog/{blogId}"
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			part=f"item/{wikiId}"
		else: raise exceptions.SpecifyType

		data = dumps(data)
		response = await self.make_request(method="POST", endpoint=f"/g/s/{part}/g-comment", data=data, headers=self.get_headers(data=data))
		return response.status

	async def delete_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None) -> int:

		if userId:part=f"user-profile/{userId}"
		elif blogId:part=f"blog/{blogId}"
		elif wikiId:part=f"item/{wikiId}"
		else: raise exceptions.SpecifyType

		response = await self.make_request(method="DELETE", endpoint=f"/g/s/{part}/g-comment/{commentId}", headers=self.get_headers())
		return response.status



	async def like_blog(self, blogId: Union[str, list] = None, wikiId: str = None) -> int:

		data = {
			"value": 4,
			"timestamp": int(timestamp() * 1000)
		}

		if blogId:
			if isinstance(blogId, str):
				data["eventSource"] = "UserProfileView"
				data = dumps(data)
				response = await self.make_request(method="POST", endpoint=f"/g/s/blog/{blogId}/g-vote?cv=1.2", data=data, headers=self.get_headers(data=data))
			elif isinstance(blogId, list):
				data["targetIdList"] = blogId
				data = dumps(data)
				response = await self.make_request(method="POST", endpoint=f"/g/s/feed/g-vote", data=data, headers=self.get_headers(data=data))
			else: raise exceptions.WrongType(type(blogId))

		elif wikiId:
			data["eventSource"] = "PostDetailView"
			data = dumps(data)
			response = await self.make_request(method="POST", endpoint=f"/g/s/item/{wikiId}/g-vote?cv=1.2", data=data, headers=self.get_headers(data=data))
		else: raise exceptions.SpecifyType()
		return response.status


	async def unlike_blog(self, blogId: str = None, wikiId: str = None) -> int:

		if blogId: url=f"/g/s/blog/{blogId}/g-vote?eventSource=UserProfileView"
		elif wikiId: url=f"/g/s/item/{wikiId}/g-vote?eventSource=PostDetailView"
		else: raise exceptions.SpecifyType

		response = await self.make_request(method="POST", endpoint=url, headers=self.get_headers())
		response.status

	async def like_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None) -> int:

		data = {
			"value": 4,
			"timestamp": int(timestamp() * 1000)
		}
		if userId:
			data["eventSource"] = "UserProfileView"
			part=f"user-profile/{userId}"
		elif blogId:
			data["eventSource"] = "PostDetailView"
			part=f"blog/{blogId}"
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			part=f"item/{wikiId}"
		else: raise exceptions.SpecifyType

		data = dumps(data)
		response = await self.make_request(method="POST", endpoint=f"/g/s/{part}/comment/{commentId}/g-vote?cv=1.2&value=1", data=data, headers=self.get_headers(data=data))
		return response.status


	async def unlike_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None) -> int:

		if userId:part=f"user-profile/{userId}"
		elif blogId:part=f"blog/{blogId}"
		elif wikiId:part=f"item/{wikiId}"
		else: raise exceptions.SpecifyType

		response = await self.make_request(method="DELETE", endpoint=f"/g/s/{part}/comment/{commentId}/g-vote?eventSource={'UserProfileView' if userId else 'PostDetailView'}", headers=self.get_headers())
		return response.status

	async def get_ta_announcements(self, language: str = None, start: int = 0, size: int = 25) -> AsyncObjectCreator:

		language = language if language else self.language
		supported_languages = await self.get_supported_languages(size=100).supportedLanguages
		if language not in supported_languages: raise exceptions.UnsupportedLanguage(language)
		response = await self.make_request(method="GET", endpoint=f"/g/s/announcement?language={language}&start={start}&size={size}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())



#OTHER=============================
	async def upload_media(self, file: AsyncBufferedReader, fileType: str) -> dict:

		if fileType == "audio":fileType = "audio/aac"
		elif fileType == "image":fileType = "image/jpg"
		else: raise exceptions.SpecifyType(fileType)
		data = await file.read()

		response = await self.make_request(method="POST", endpoint="/g/s/media/upload", data=data, headers=self.get_headers(data=data, content_type=fileType))
		json = await response.json()
		return json["mediaValue"]


	async def get_supported_languages(self, start: int = 0, size: int = 25) -> AsyncObjectCreator:

		response = await self.make_request(method="GET", endpoint=f"/g/s/community-collection/supported-languages?start={start}&size={size}", headers=self.get_headers())
		return AsyncObjectCreator(await response.json())


	async def watch_ad(self, userId: str = None) -> int:

		data = dumps(tapjoy(userId if userId else self.profile.userId))
		response = await self.session.post("https://ads.tapdaq.com/v4/analytics/reward", data=data, headers=tapjoy_headers())
		return exceptions.check_exceptions(response.text) if response.status != 204 else response.status


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