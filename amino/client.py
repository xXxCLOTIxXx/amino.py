from .socket import SocketHandler, Callbacks
from .helpers.requester import Requester
from .helpers.headers import headers, tapjoy, tapjoy_headers
from .models.objects import profile
from .models import objects
from .helpers import exceptions
from .helpers.generators import generate_deviceId, sid_to_uid

from requests import Session
from time import time as timestamp
from json import dumps
from time import timezone
from locale import getdefaultlocale as locale
from base64 import b64encode
from threading import Thread
from uuid import UUID
from os import urandom
from typing import BinaryIO, Union
from binascii import hexlify





class Client(SocketHandler, Requester, Callbacks):
	profile = profile()
	active_live_chats = list()

	def __init__(self, deviceId: str = None, auto_device: bool = False, language: str = "en", user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2", socket_enabled: bool = True, socket_debug: bool = False, socket_trace: bool = False, socket_whitelist_communities: list = None, socket_old_message_mode: bool = False, proxies: dict = None, certificate_path = None):
		Requester.__init__(self, session=Session(), proxies=proxies, verify=certificate_path)
		self.socket_enabled=socket_enabled
		if socket_enabled:
			SocketHandler.__init__(self, old_message_mode=socket_old_message_mode, whitelist_communities=socket_whitelist_communities, sock_trace=socket_trace, debug=socket_debug)
			Callbacks.__init__(self)
		self.device_id = deviceId if deviceId else generate_deviceId()
		self.auto_device = auto_device
		self.user_agent=user_agent
		self.language=language


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
	def login(self, email: str, password: str = None, secret: str = None) -> profile:
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

		response = self.make_request(method="POST", endpoint="/g/s/auth/login", body=data, headers=self.get_headers(data=data, deviceId=deviceId)).json()
		self.profile = profile(response)
		if self.socket_enabled:self.connect()
		return self.profile


	def login_phone(self, phone: str, password: str) -> profile:

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

		response = self.make_request(method="POST", endpoint="/g/s/auth/login", body=data, headers=self.get_headers(data=data, deviceId=deviceId)).json()
		self.profile = profile(response)
		if self.socket_enabled:self.connect()
		return self.profile


	def login_sid(self, sid: str, need_account_info: bool = False) -> profile:
		if need_account_info:
			self.profile=profile({"sid": sid, "auid": sid_to_uid(sid), "userProfile": self.get_user_info(sid_to_uid(sid)).json})
		else:
			self.profile=profile({"sid": sid, "auid": sid_to_uid(sid)})
		if self.socket_enabled:self.connect()
		return self.profile




	def register_account(self, nickname: str, email: str, password: str, verificationCode: str, deviceId: str = None, timeout: int = None) -> dict:

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
		response = self.make_request(method="POST", endpoint="/g/s/auth/register", body=data, headers=self.get_headers(data=data, deviceId=deviceId), timeout=timeout).json()
		return response



	def restore_account(self, email: str, password: str) -> int:

		deviceId = self.deviceId
		data = dumps({
			"secret": f"0 {password}",
			"deviceID": deviceId,
			"email": email,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint="/g/s/account/delete-request/cancel", body=data, headers=self.get_headers(data=data, deviceId=deviceId))
		return response.status_code



	def logout(self) -> int:

		deviceId = self.deviceId
		data = dumps({
			"deviceID": deviceId,
			"clientType": 100,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint="/g/s/auth/logout", body=data, headers=self.get_headers(data=data, deviceId=deviceId))
		self.profile = profile()
		if self.socket_enabled:self.close()
		return response.status_code

	def configure_account(self, age: int, gender: str) -> int:

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

		response = self.make_request(method="POST", endpoint="/g/s/persona/profile/basic", body=data, headers=self.get_headers(data=data))
		return response.status_code

	def set_amino_id(self, aminoId: str) -> int:

		data = dumps({
			"aminoId": aminoId,
			"timestamp": int(timestamp() * 1000)
			})

		response = self.make_request(method="POST", endpoint="/g/s/account/change-amino-id", body=data, headers=self.get_headers(data=data))
		return response.status_code


	def set_privacy_status(self, isAnonymous: bool = False, getNotifications: bool = False):

		data = {
			"timestamp": int(timestamp() * 1000),
			"privacyMode": 2 if isAnonymous else 1
			}
		if not getNotifications: data["notificationStatus"] = 2
		else: data["privacyMode"] = 1

		data = dumps(data)
		response = self.make_request(method="POST", endpoint="/g/s/account/visit-settings", body=data, headers=self.get_headers(data=data))
		return response.status_code




	def verify_email(self, email: str, code: str) -> int:

		deviceId = self.deviceId
		data = dumps({
			"validationContext": {
				"type": 1,
				"identity": email,
				"data": {"code": code}},
			"deviceID": deviceId,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint="/g/s/auth/check-security-validation", body=data, headers=self.get_headers(data=data, deviceId=deviceId))
		return response.status_code



	def request_verify_code(self, email: str, resetPassword: bool = False, timeout: int = None) -> int:

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

		response = self.make_request(method="POST", endpoint="/g/s/auth/request-security-validation", body=data, headers=self.get_headers(data=data, deviceId=deviceId), timeout=timeout)
		return response.status_code


	def activate_account(self, email: str, code: str) -> int:

		deviceId = self.deviceId
		data = dumps({
			"type": 1,
			"identity": email,
			"data": {"code": code},
			"deviceID": deviceId
		})

		response = self.make_request(method="POST", endpoint="/g/s/auth/activate-email", body=data, headers=self.get_headers(data=data, deviceId=deviceId))
		return response.status_code




	def delete_account(self, password: str) -> int:

		deviceId = self.deviceId
		data = dumps({
			"deviceID":deviceId,
			"secret": f"0 {password}"
		})

		response = self.make_request(method="POST", endpoint="/g/s/account/delete-request", body=data, headers=self.get_headers(data=data, deviceId=deviceId))
		return response.status_code


	def change_password(self, email: str, password: str, code: str) -> int:

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

		response = self.make_request(method="POST", endpoint="/g/s/auth/reset-password", body=data, headers=self.get_headers(data=data, deviceId=deviceId))
		return response.status_code


	def check_deviceId(self, deviceId: str) -> tuple:

		data = dumps({
			"deviceID": deviceId,
			"bundleID": "com.narvii.amino.master",
			"clientType": 100,
			"timezone": -timezone // 1000,
			"systemPushEnabled": True,
			"locale": locale()[0],
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint="/g/s/device", body=data, headers=self.get_headers(data=data, deviceId=deviceId), successfully=None)
		try:response_data = response.json()
		except:response_data = response.text
		return (response.status_code, response_data)


	def edit_profile(self, nickname: str = None, content: str = None, icon: BinaryIO = None, backgroundColor: str = None, backgroundImage: str = None, defaultBubbleId: str = None) -> int:

		data = {
			"address": None,
			"latitude": 0,
			"longitude": 0,
			"mediaList": None,
			"eventSource": "UserProfileView",
			"timestamp": int(timestamp() * 1000)
		}

		if nickname: data["nickname"] = nickname
		if icon: data["icon"] = self.upload_media(icon, "image")
		if content: data["content"] = content
		if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if backgroundImage: data["extensions"] = {"style": {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}}
		if defaultBubbleId: data["extensions"] = {"defaultBubbleId": defaultBubbleId}

		data = dumps(data)
		response = self.make_request(method="POST", endpoint=f"/g/s/user-profile/{self.profile.userId}", body=data, headers=self.get_headers(data=data))
		return response.status_code

	def get_eventlog(self) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/eventlog/profile?language={self.language}", headers=self.get_headers()).json()
		return response


	def get_account_info(self) -> objects.UserProfile:

		response = self.make_request(method="GET", endpoint="/g/s/account", headers=self.get_headers()).json()
		return objects.UserProfile(response["account"])




#WALLET/COINS=============================
	def get_membership_info(self) -> dict:

		response = self.make_request(method="GET", endpoint="/g/s/membership?force=true", headers=self.get_headers()).json()
		return response


	def get_wallet_info(self) -> dict:

		response = self.make_request(method="GET", endpoint="/g/s/wallet", headers=self.get_headers()).json()
		return response["wallet"]


	def get_wallet_history(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/wallet/coin/history?start={start}&size={size}", headers=self.get_headers()).json()
		return response["coinHistoryList"]

	def wallet_config(self, level: int) -> int:


		data = dumps({
			"adsLevel": level,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/g/s/wallet/ads/config", data=data, headers=self.get_headers(data=data))
		return response.status_code

	def buy_in_store(self, objectId: str, isAutoRenew: bool = False) -> int:
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

		response = self.make_request(method="POST", endpoint=f"/g/s/store/purchase", data=data, headers=self.get_headers(data=data))
		return response.status_code

	def purchase(self, objectId: str, isAutoRenew: bool = False) -> int:
		return self.buy_in_store(objectId=objectId, isAutoRenew=isAutoRenew)


	def send_coins(self, coins: int, blogId: str = None, chatId: str = None, objectId: str = None, transactionId: str = None):

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
		response = self.make_request(method="POST", endpoint=url, data=data, headers=self.get_headers(data=data))
		return response.status_code

	def claim_new_user_coupon(self) -> int:

		response = self.make_request(method="POST", endpoint="/g/s/coupon/new-user-coupon/claim", headers=self.get_headers())
		return response.status_code


	def get_subscriptions(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/store/subscription?objectType=122&start={start}&size={size}", headers=self.get_headers()).json()
		return response["storeSubscriptionItemList"]



#OBJECTS=============================
	def get_from_link(self, link: str) -> objects.FromCode:

		response = self.make_request(method="GET", endpoint=f"/g/s/link-resolution?q={link}", headers=self.get_headers()).json()
		return objects.FromCode(response["linkInfoV2"])
	
	def link_identify(self, link: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/community/link-identify?q=http%3A%2F%2Faminoapps.com%2Finvite%2F{code}", headers=self.get_headers()).json()
		return response

	def get_from_deviceId(self, deviceId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/auid?deviceId={deviceId}", headers=self.get_headers()).json()
		return response


	def get_from_Id(self, objectId: str, objectType: int, comId: str = None):

		data = json.dumps({
			"objectId": objectId,
			"targetCode": 1,
			"objectType": objectType,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="GET", endpoint=f"/g/{f's-x{comId}' if comId else 's'}/link-resolution", data=data, headers=self.get_headers(data=data)).json()
		return objects.FromCode(response["linkInfoV2"])




#USERS=============================
	def get_user_info(self, userId: str) -> objects.UserProfile:

		response = self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}", headers=self.get_headers()).json()
		return objects.UserProfile(response["userProfile"])

	def get_all_users(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/user-profile?type=recent&start={start}&size={size}", headers=self.get_headers()).json()
		return response


	def get_user_following(self, userId: str, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/joined?start={start}&size={size}", headers=self.get_headers()).json()
		return response["userProfileList"]

	def get_user_followers(self, userId: str, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/member?start={start}&size={size}", headers=self.get_headers()).json()
		return response["userProfileList"]

	def get_user_visitors(self, userId: str, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/visitors?start={start}&size={size}", headers=self.get_headers()).json()
		return response


	def get_blocked_users(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/block?start={start}&size={size}", headers=self.get_headers()).json()
		return response["userProfileList"]


	def get_blocker_users(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/block/full-list?start={start}&size={size}", headers=self.get_headers()).json()
		return response["blockerUidList"]


	def get_wall_comments(self, userId: str, sorting: str, start: int = 0, size: int = 25) -> dict:

		if sorting.lower() not in ("newest", "oldest", "vote"): raise exceptions.WrongType(sorting)
		response = self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/g-comment?sort={sorting}&start={start}&size={size}", headers=self.get_headers()).json()
		return response["commentList"]

	def visit(self, userId: str) -> int:

		response = self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}?action=visit", headers=self.get_headers())
		return response.status_code

	def follow(self, userId: Union[str, list]) -> int:

		if isinstance(userId, str):
			response = self.make_request(method="POST", endpoint=f"/g/s/user-profile/{userId}/member", headers=self.get_headers())
		elif isinstance(userId, list):
			data = dumps({"targetUidList": userId, "timestamp": int(timestamp() * 1000)})
			response = self.make_request(method="POST", endpoint=f"/g/s/user-profile/{self.profile.userId}/joined", data=data, headers=self.get_headers(data=data))
		else: raise exceptions.WrongType(userId)
		return response.status_code


	def unfollow(self, userId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/g/s/user-profile/{userId}/member/{self.profile.userId}", headers=self.get_headers())
		return response.status_code


	def block(self, userId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/g/s/block/{userId}", headers=self.get_headers())
		return response.status_code

	def unblock(self, userId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/g/s/block/{userId}", headers=self.get_headers())
		return response.status_code




#COMMYNITY=============================
	def get_my_communites(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/community/joined?v=1&start={start}&size={size}", headers=self.get_headers()).json()
		return response

	def get_public_communities(self, language: str = None, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/topic/0/feed/community?language={language if language else self.language}&type=web-explore&categoryKey=recommendation&size={size}&pagingType=t", headers=self.get_headers()).json()
		return response["communityList"]


	def get_community_info(self, comId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s-x{comId}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount", headers=self.get_headers()).json()
		return response["community"]


	def search_community(self, aminoId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/search/amino-id-and-link?q={aminoId}", headers=self.get_headers()).json()
		return response["resultList"]

	def join_community(self, comId: str, invitationId: str = None) -> int:

		data = {"timestamp": int(timestamp() * 1000)}
		if invitationId: data["invitationId"] = invitationId
		data = dumps(data)

		response = self.make_request(method="POST", endpoint=f"/x{comId}/s/community/join", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def request_join_community(self, comId: str, message: str = None) -> int:

		data = dumps({
			"message": message,
			"timestamp": int(timestamp() * 1000)
			})

		response = self.make_request(method="POST", endpoint=f"/x{comId}/s/community/membership-request", data=data, headers=self.get_headers(data=data))
		return response.status_code

	def leave_community(self, comId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/x{comId}/s/community/leave", headers=self.get_headers())
		return response.status_code



	def flag_community(self, comId: str, reason: str, flagType: int, isGuest: bool = False) -> int:
		return self.flag(reason=reason, flagType=flagType, isGuest=isGuest, comId=comId)


	def reorder_linked_communities(self, comIds: list) -> int:

		data = dumps({
			"ndcIds": comIds,
			"timestamp": int(timestamp() * 1000)
			})

		response = self.make_request(method="POST", endpoint=f"/g/s/user-profile/{self.profile.userId}/linked-community/reorder", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def add_linked_community(self, comId: str):

		response = self.make_request(method="POST", endpoint=f"/g/s/user-profile/{self.profile.userId}/linked-community/{comId}", headers=self.get_headers())
		return response.status_code


	def remove_linked_community(self, comId: str):

		response = self.make_request(method="DELETE", endpoint=f"/g/s/user-profile/{self.profile.userId}/linked-community/{comId}", headers=self.get_headers())
		return response.status_code


	def get_linked_communities(self, userId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/linked-community", headers=self.get_headers()).json()
		return response["linkedCommunityList"]



	def get_unlinked_communities(self, userId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/linked-community", headers=self.get_headers()).json()
		return response["unlinkedCommunityList"]



#CHAT=============================
	def start_chat(self, userId: Union[str, list], message: str, title: str = None, content: str = None, isGlobal: bool = False, publishToGlobal: bool = False) -> dict:

		if isinstance(userId, str): userIds = [userId]
		elif isinstance(userId, list): userIds = userId
		else: raise exceptions.WrongType()

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
		response = self.make_request(method="POST", endpoint=f"/g/s/chat/thread", data=data, headers=self.get_headers(data=data)).json()
		return response["thread"]


	def edit_chat(self, chatId: str, doNotDisturb: bool = None, pinChat: bool = None, title: str = None, icon: str = None, backgroundImage: str = None, content: str = None, announcement: str = None, coHosts: list = None, keywords: list = None, pinAnnouncement: bool = None, publishToGlobal: bool = None, canTip: bool = None, viewOnly: bool = None, canInvite: bool = None, fansOnly: bool = None):
		#Not completed
		pass


	def get_my_chats(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/chat/thread?type=joined-me&start={start}&size={size}", headers=self.get_headers()).json()
		return response["threadList"]


	def get_chat_thread(self, chatId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/chat/thread/{chatId}", headers=self.get_headers()).json()
		return response["thread"]


	def get_chat_users(self, chatId: str, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2", headers=self.get_headers()).json()
		return response["memberList"]

	def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str = None) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}"+ f"&pageToken={pageToken}" if pageToken else '', headers=self.get_headers()).json()
		return response


	def get_message_info(self, chatId: str, messageId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s/chat/thread/{chatId}/message/{messageId}", headers=self.get_headers()).json()
		return response["message"]


	def join_chat(self, chatId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/member/{self.profile.userId}", headers=self.get_headers(content_type="application/x-www-form-urlencoded"))
		return response.status_code

	def leave_chat(self, chatId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/g/s/chat/thread/{chatId}/member/{self.profile.userId}", headers=self.get_headers())
		return response.status_code

	def invite_to_chat(self, userId: Union[str, list], chatId: str) -> int:

		if isinstance(userId, str): userIds = [userId]
		elif isinstance(userId, list): userIds = userId
		else: raise exceptions.WrongType()

		data = dumps({
			"uids": userIds,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/member/invite", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def kick(self, userId: str, chatId: str, allowRejoin: bool = True) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/g/s/chat/thread/{chatId}/member/{userId}?allowRejoin={1 if allowRejoin else 0}", data=data, headers=self.get_headers(data=data))
		return response.status_code



	def accept_host(self, chatId: str, requestId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept", data=dumps({}), headers=self.get_headers(data=dumps({})))
		return response.status_code


	def invite_to_vc(self, chatId: str, userId: str) -> int:

		data = dumps({
			"uid": userId
		})

		response = self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/vvchat-presenter/invite", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def mark_as_read(self, chatId: str, messageId: str):

		data = dumps({
			"messageId": messageId,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/mark-as-read", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def send_message(self, chatId: str, message: str = None, messageType: int = 0, file: BinaryIO = None, fileType: str = None, replyTo: str = None, mentionUserIds: list = None, stickerId: str = None, embedId: str = None, embedType: int = None, embedLink: str = None, embedTitle: str = None, embedContent: str = None, embedImage: BinaryIO = None):

		if message is not None and file is None:
			message = message.replace("<@", "‎‏").replace("@>", "‬‭")

		mentions = []
		if mentionUserIds:
			for mention_uid in mentionUserIds:
				mentions.append({"uid": mention_uid})

		if embedImage:
			embedImage = [[100, self.upload_media(embedImage, "image"), None]]

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

			data["mediaUploadValue"] = base64.b64encode(file.read()).decode()

		data = dumps(data)
		response = self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/message", data=data, headers=self.get_headers(data=data))
		return response.status_code

	def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str = None):

		data = {
			"adminOpName": 102,
			"adminOpNote": {"content": reason},
			"timestamp": int(timestamp() * 1000)
		}

		data = dumps(data)
		if not asStaff:response = self.make_request(method="DELETE", endpoint=f"/g/s/chat/thread/{chatId}/message/{messageId}", headers=self.get_headers())
		else:response = self.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/message/{messageId}/admin", data=data, headers=self.get_headers(data=data))
		return response.status_code




#BLOGS AND ECT=============================
	def flag(self, reason: str, flagType: int, userId: str = None, blogId: str = None, wikiId: str = None, comId: str = None, asGuest: bool = False) -> int:

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
		response = self.make_request(method="POST", endpoint=f"/g/s/{'g-flag' if isGuest else 'flag'}", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def get_blog_info(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None) -> dict:


		if fileId:part=f"shared-folder/files/{fileId}"
		elif blogId or quizId:part=f"blog/{blogId}"
		elif wikiId:part=f"item/{wikiId}"
		else: raise exceptions.SpecifyType

		response = self.make_request(method="GET", endpoint=f"/g/s/{part}", headers=self.get_headers()).json()
		return response.get("file", response)


	def get_blog_comments(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, sorting: str = "newest", start: int = 0, size: int = 25):

		if sorting.lower() not in ("newest", "oldest", "vote"): raise exceptions.WrongType(sorting)
		if fileId:part=f"shared-folder/files/{fileId}"
		elif blogId or quizId:part=f"blog/{blogId}"
		elif wikiId:part=f"item/{wikiId}"
		else: raise exceptions.SpecifyType

		response = self.make_request(method="GET", endpoint=f"/g/s/{part}/comment?sort={sorting}&start={start}&size={size}", headers=self.get_headers()).json()
		return response["commentList"]



	def comment(self, message: str, userId: str = None, blogId: str = None, wikiId: str = None, replyTo: str = None) -> int:

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
		response = self.make_request(method="POST", endpoint=f"/g/s/{part}/g-comment", data=data, headers=self.get_headers(data=data))
		return response.status_code

	def delete_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None) -> int:

		if userId:part=f"user-profile/{userId}"
		elif blogId:part=f"blog/{blogId}"
		elif wikiId:part=f"item/{wikiId}"
		else: raise exceptions.SpecifyType

		response = self.make_request(method="DELETE", endpoint=f"/g/s/{part}/g-comment/{commentId}", headers=self.get_headers())
		return response.status_code



	def like_blog(self, blogId: Union[str, list] = None, wikiId: str = None) -> int:

		data = {
			"value": 4,
			"timestamp": int(timestamp() * 1000)
		}

		if blogId:
			if isinstance(blogId, str):
				data["eventSource"] = "UserProfileView"
				data = dumps(data)
				response = self.make_request(method="POST", endpoint=f"/g/s/blog/{blogId}/g-vote?cv=1.2", data=data, headers=self.get_headers(data=data))
			elif isinstance(blogId, list):
				data["targetIdList"] = blogId
				data = dumps(data)
				response = self.make_request(method="POST", endpoint=f"/g/s/feed/g-vote", data=data, headers=self.get_headers(data=data))
			else: raise exceptions.WrongType(type(blogId))

		elif wikiId:
			data["eventSource"] = "PostDetailView"
			data = dumps(data)
			response = self.make_request(method="POST", endpoint=f"/g/s/item/{wikiId}/g-vote?cv=1.2", data=data, headers=self.get_headers(data=data))
		else: raise exceptions.SpecifyType()
		return response.status_code


	def unlike_blog(self, blogId: str = None, wikiId: str = None) -> int:

		if blogId: url=f"/g/s/blog/{blogId}/g-vote?eventSource=UserProfileView"
		elif wikiId: url=f"/g/s/item/{wikiId}/g-vote?eventSource=PostDetailView"
		else: raise exceptions.SpecifyType

		response = self.make_request(method="POST", endpoint=url, headers=self.get_headers())
		response.status_code

	def like_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None) -> int:

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
		response = self.make_request(method="POST", endpoint=f"/g/s/{part}/comment/{commentId}/g-vote?cv=1.2&value=1", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def unlike_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None) -> int:

		if userId:part=f"user-profile/{userId}"
		elif blogId:part=f"blog/{blogId}"
		elif wikiId:part=f"item/{wikiId}"
		else: raise exceptions.SpecifyType

		response = self.make_request(method="DELETE", endpoint=f"/g/s/{part}/comment/{commentId}/g-vote?eventSource={'UserProfileView' if userId else 'PostDetailView'}", headers=self.get_headers())
		return response.status_code

	def get_ta_announcements(self, language: str = None, start: int = 0, size: int = 25) -> dict:

		language = language if language else self.language
		if language not in self.get_supported_languages(size=100): raise exceptions.UnsupportedLanguage(language)
		response = self.make_request(method="POST", endpoint=f"/g/s/announcement?language={language}&start={start}&size={size}", headers=self.get_headers()).json()
		return response["blogList"]



#OTHER=============================
	def upload_media(self, file: BinaryIO, fileType: str) -> int:

		if fileType == "audio":fileType = "audio/aac"
		elif fileType == "image":fileType = "image/jpg"
		else: raise exceptions.SpecifyType(fileType)
		data = file.read()

		response = self.make_request(method="POST", endpoint="/g/s/media/upload", body=data, headers=self.get_headers(data=data, content_type=fileType)).json()
		return response["mediaValue"]


	def get_supported_languages(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="POST", endpoint=f"/g/s/community-collection/supported-languages?start={start}&size={size}", headers=self.get_headers()).json()
		return response["supportedLanguages"]


	def watch_ad(self, userId: str = None) -> int:

		data = dumps(tapjoy(userId if userId else self.profile.userId))
		response = self.session.post("https://ads.tapdaq.com/v4/analytics/reward", data=data, headers=tapjoy_headers())
		return exceptions.check_exceptions(response.text) if response.status != 204 else response.status_code



#SOCKET=============================
	def create_socket_event(self, data):
		return self.resolve(data)


	def online(self, comId: int):
		self.online_list.add(comId)

	def offline(self, comId: int):
		try:self.online_list.remove(comId)
		except KeyError:pass


	def typing_start(self, chatId: str, comId: int = None):

		data = {
			"actions": ["Typing"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		if comId:data["ndcId"]=comId
		self.send_action(message_type=304, body=data)



	def typing_end(self, chatId: str, comId: int = None):

		data = {
			"actions": ["Typing"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		if comId:data["ndcId"]=comId
		self.send_action(message_type=306, body=data)


	def recording_start(self, chatId: str, comId: int = None):

		data = {
			"actions": ["Recording"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		if comId:data["ndcId"]=comId
		self.send_action(message_type=304, body=data)

	def recording_end(self, chatId: str, comId: int = None):

		data = {
			"actions": ["Recording"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		if comId:data["ndcId"]=comId
		self.send_action(message_type=306, body=data)


	def join_live_chat(self, chatId: str, comId: int = None, as_viewer: bool = False):

		data = {
			"threadId": chatId,
			"joinRole": 2 if as_viewer else 1,
		}
		if comId:data["ndcId"]=int(comId)
		self.send_action(message_type=112, body=data)



	def start_vc(self, chatId: str, comId: int = None, join_as_viewer: bool = False):
		self.join_live_chat(chatId=chatId, comId=comId, as_viewer=join_as_viewer)
		data = {
			"threadId": chatId,
			"channelType": 1
		}
		if comId:data["ndcId"]=int(comId)
		self.send_action(message_type=108, body=data)

		self.active_live_chats.append(chatId)
		Thread(target=self.vc_loop, args=(comId, chatId, join_as_viewer)).start()

	def end_vc(self, chatId: str, comId: int = None):
		self.join_live_chat(chatId=chatId, comId=comId, as_viewer=True)
		self.leave_from_live_chat(chatId)

	def leave_from_live_chat(self, chatId: str):
		if chatId in self.active_live_chats:
			self.active_live_chats.remove(chatId)