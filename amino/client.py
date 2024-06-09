from .objects.auth_data import auth_data
from .helpers.requests_builder import requestsBuilder
from .helpers.generator import generate_deviceId, sid_to_uid
from .helpers.exceptions import SpecifyType, WrongType, UnsupportedLanguage
from .ws.socket import Socket
from .objects.reqObjects import DynamicObject

from .objects.args import Gender, UploadType, Sorting, MessageTypes

from time import time
from typing import Union, BinaryIO
from base64 import b64encode
from uuid import uuid4
from mimetypes import guess_type


class Client(Socket):
	req: requestsBuilder
	socket_enable = True

	def __init__(self, deviceId: str = None, language: str = "en", user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2", proxies: dict = None, socket_enable: bool = True, sock_trace: bool = False, sock_debug: bool = False):
		self.req = requestsBuilder(
			proxies=proxies,
			profile=auth_data(
				deviceId=deviceId if deviceId else generate_deviceId(),
				language=language,
				user_agent=user_agent
			)
		)
		self.socket_enable = socket_enable
		Socket.__init__(self, sock_trace, sock_debug)


	def __repr__(self):
		return repr(f"class Client <sid={self.sid}, userId={self.userId}, deviceId={self.deviceId}, user_agent={self.profile.user_agent}, language={self.language}>")

	
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
	

	@property
	def language(self):
		return self.req.profile.language



	def login(self, email: str, password: str = None, secret: str = None) -> DynamicObject:
		if password is None and secret is None: raise SpecifyType
		result = self.req.request("POST", "/g/s/auth/login", {
			"email": email,
			"v": 2,
			"secret": secret if secret else f"0 {password}",
			"deviceID": self.deviceId,
			"clientType": 100,
			"action": "normal",
		})
		self.req.profile.sid, self.req.profile.uid = result["sid"], result["auid"]
		if self.socket_enable:
			final = f"{self.deviceId}|{int(time() * 1000)}"
			self.ws_connect(final=final, headers=self.ws_headers(self.sid, final, self.deviceId))
		return result["userProfile"]


	def login_phone(self, phone: str, password: str = None, secret: str = None) -> DynamicObject:
		if password is None and secret is None: raise SpecifyType
		result = self.req.request("POST", "/g/s/auth/login", {
			"phoneNumber": phone,
			"v": 2,
			"secret": secret if secret else f"0 {password}",
			"deviceID": self.deviceId,
			"clientType": 100,
			"action": "normal",
		})
		self.req.profile.sid, self.req.profile.uid = result["sid"], result["auid"]
		if self.socket_enable:
			final = f"{self.deviceId}|{int(time() * 1000)}"
			self.ws_connect(final=final, headers=self.ws_headers(self.sid, final, self.deviceId))
		return result["userProfile"]

	
	def login_sid(self, sid: str) -> auth_data:
		self.req.profile.sid, self.req.profile.uid = sid, sid_to_uid(sid)
		if self.socket_enable:
			final = f"{self.deviceId}|{int(time() * 1000)}"
			self.ws_connect(final=final, headers=self.ws_headers(self.sid, final, self.deviceId))
		return self.profile



	def logout(self) -> DynamicObject:
		result = self.req.request("POST", "/g/s/auth/logout", {
			"deviceID": self.profile.deviceId,
			"clientType": 100,
		})
		self.req.profile.sid, self.req.profile.uid = None, None
		if self.socket_enable:self.ws_disconnect()
		return result

	def restore_account(self, email: str, password: str) -> DynamicObject:
		return self.req.request("POST", "/g/s/account/delete-request/cancel", {
			"secret": f"0 {password}",
			"deviceID": self.deviceId,
			"email": email,
		})

	def configure_profile(self, age: int, gender: int = Gender.non_binary) -> DynamicObject:
		if gender not in Gender.all:raise SpecifyType
		return self.req.request("POST", "/g/s/persona/profile/basic", {
			"age": max(13, age),
			"gender": gender,
		})	


	def verify_account(self, email: str, code: str) -> DynamicObject:
		return self.req.request("POST", "/g/s/auth/check-security-validation", {
			"validationContext": {
				"type": 1,
				"identity": email,
				"data": {"code": code}},
			"deviceID": self.deviceId,
		})


	def request_verify_code(self, email: str, resetPassword: bool = False) -> DynamicObject:
		data = {
			"identity": email,
			"type": 1,
			"deviceID": self.deviceId,
		}
		if resetPassword is True:
			data["level"] = 2
			data["purpose"] = "reset-password"
		return self.req.request("POST", "/g/s/auth/request-security-validation", data)

	def activate_account(self, email: str, code: str) -> DynamicObject:
		return self.req.request("POST", "/g/s/auth/activate-email", {
			"type": 1,
			"identity": email,
			"data": {"code": code},
			"deviceID": self.deviceId,
		})


	def delete_account(self, password: str) -> DynamicObject:
		return self.req.request("POST", "/g/s/account/delete-request", {
			"deviceID": self.deviceId,
			"secret": f"0 {password}",
		})


	def change_password(self, email: str, password: str, code: str) -> DynamicObject:
		return self.req.request("POST", "/g/s/auth/reset-password", {
			"updateSecret": f"0 {password}",
			"emailValidationContext": {
				"data": {
					"code": code
				},
				"type": 1,
				"identity": email,
				"level": 2,
				"deviceID": self.deviceId
			},
			"phoneNumberValidationContext": None,
			"deviceID": self.deviceId,
		})

	def get_eventlog(self) -> DynamicObject:
		return self.req.request("GET", f"/g/s/eventlog/profile?language={self.language}")



	def get_account_info(self):
		return self.req.request("GET", "/g/s/account")["account"]


	def my_communities(self, start: int = 0, size: int = 25) -> DynamicObject:
		return self.req.request("GET", f"/g/s/community/joined?v=1&start={start}&size={size}")["communityList"]


	def profiles_in_communities(self, start: int = 0, size: int = 25) -> DynamicObject:
		return self.req.request("GET", f"/g/s/community/joined?v=1&start={start}&size={size}")["userInfoInCommunities"]


	def get_user_info(self, userId: str):
		return self.req.request("GET", f"/g/s/user-profile/{userId}")["userProfile"]

	def get_my_chats(self, start: int = 0, size: int = 25) -> DynamicObject:
		return self.req.request("GET", f"/g/s/chat/thread?type=joined-me&start={start}&size={size}")["threadList"]

	def get_chat(self, chatId: str) -> DynamicObject:
		return self.req.request("GET", f"/g/s/chat/thread/{chatId}")["thread"]

	def get_chat_users(self, chatId: str, start: int = 0, size: int = 25) -> DynamicObject:
		return self.req.request("GET", f"/g/s/chat/thread/{chatId}/member?cv=1.2&type=default&start={start}&size={size}")["memberList"]

	def join_chat(self, chatId: str) -> DynamicObject:
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/member/{self.userId}")

	def leave_chat(self, chatId: str):
		return self.req.request("DELETE", f"/g/s/chat/thread/{chatId}/member/{self.userId}")

	def start_chat(self, userId: Union[str, list, tuple], message: str, title: str = None, content: str = None, isGlobal: bool = False, publishToGlobal: bool = False) -> DynamicObject:
		if isinstance(userId, (str, list, tuple)):userIds = list(userId)
		else:raise WrongType(type(userId))
		data = {
			"title": title,
			"inviteeUids": userIds,
			"initialMessageContent": message,
			"content": content,
			"type": 2 if isGlobal else 0,
			"publishToGlobal": 1 if publishToGlobal else 0,
		}
		if isGlobal:data["eventSource"] = "GlobalComposeMenu"
		return self.req.request("POST", f"/g/s/chat/thread", data=data)["thread"]

	def invite_to_chat(self, userId: Union[str, list], chatId: str) -> DynamicObject:
		if not isinstance(userId, (str, list)):raise WrongType(type(userId))
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/member/invite", {
			"uids": list(userId) if isinstance(userId, str) else userId,
		})


	def kick(self, userId: str, chatId: str, allowRejoin: bool = True) -> DynamicObject:
		return self.req.request("DELETE", f"/g/s/chat/thread/{chatId}/member/{userId}?allowRejoin={int(allowRejoin)}")

	def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str = None) -> DynamicObject:
		return self.req.request("GET", f"/g/s/chat/thread/{chatId}/message?pagingType=t&size={size}{f'&pageToken={pageToken}' if pageToken else ''}")

	def get_message_info(self, chatId: str, messageId: str) -> DynamicObject:
		return self.req.request("GET", f"/g/s/chat/thread/{chatId}/message/{messageId}")["message"]

	def get_community_info(self, comId: int) -> DynamicObject:
		return self.req.request("GET", f"/g/s-x{comId}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount")["community"]

	def search_community(self, aminoId: str) -> DynamicObject:
		return self.req.request("GET", f"/g/s/search/amino-id-and-link?q={aminoId}")["resultList"]

	def get_user_following(self, userId: str, start: int = 0, size: int = 25) -> DynamicObject:
		return self.req.request("GET", f"/g/s/user-profile/{userId}/joined?start={start}&size={size}")["userProfileList"]

	def get_user_followers(self, userId: str, start: int = 0, size: int = 25) -> DynamicObject:
		return self.req.request("GET", f"/g/s/user-profile/{userId}/member?start={start}&size={size}")["userProfileList"]

	def get_blocked_users(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/g/s/block?start={start}&size={size}")["userProfileList"]

	def get_blocker_users(self, start: int = 0, size: int = 25) -> DynamicObject:
		return self.req.request("GET", f"/g/s/block/full-list?start={start}&size={size}")["blockerUidList"]
	
	def get_blog_info(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None) -> DynamicObject:

		if blogId or quizId:
			return self.req.request("GET", f"/g/s/blog/{quizId if quizId is not None else blogId}")
		if wikiId:
			return self.req.request("GET", f"/g/s/item/{wikiId}")
		if fileId:
			return self.req.request("GET", f"/g/s/shared-folder/files/{fileId}")["file"]
		raise SpecifyType()


	def get_blog_comments(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, sorting: str = Sorting.Newest, start: int = 0, size: int = 25) -> DynamicObject:
		if sorting not in Sorting.all:raise WrongType(sorting)
		if blogId or quizId:url = f"/g/s/blog/{quizId if not blogId else blogId}/comment"
		elif wikiId:url = f"/g/s/item/{wikiId}/comment"
		elif fileId:url = f"/g/s/shared-folder/files/{fileId}/comment"
		else:raise SpecifyType
		return self.req.request("GET", f"{url}?sort={sorting}&start={start}&size={size}")["commentList"]

	def get_wall_comments(self, userId: str, sorting: str = Sorting.Newest, start: int = 0, size: int = 25) -> DynamicObject:
		if sorting not in Sorting.all:raise WrongType(sorting)
		return self.req.request("GET", f"/g/s/user-profile/{userId}/g-comment?sort={sorting}&start={start}&size={size}")["commentList"]

	def flag(self, reason: str, flagType: int, userId: str = None, blogId: str = None, wikiId: str = None, asGuest: bool = False) -> DynamicObject:
		data = {
			"flagType": flagType,
			"message": reason,
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
		else:raise SpecifyType
		return self.req.request("POST", f"/g/s/{'g-flag' if asGuest else 'flag'}", data=data)




	def send_message(self, chatId: str, message: str = None, messageType: int = MessageTypes.Text, file: BinaryIO = None, replyTo: str = None, mentionUserIds: list = None, stickerId: str = None, embedId: str = None, embedType: int = None, embedLink: str = None, embedTitle: str = None, embedContent: str = None, embedImage: BinaryIO = None) -> DynamicObject:
		if message is not None:
			message = message.replace("<@", "‎‏").replace("@>", "‬‭")
		mentions = []
		if mentionUserIds:
			for mention_uid in mentionUserIds:
				mentions.append({"uid": mention_uid})
		if embedImage:embedImage = [[100, self.req.upload_media(embedImage).mediaValue, None]]
		data = {
			"type": messageType,
			"content": message,
			"clientRefId": int(time() / 10 % 1000000000),
			"attachedObject": {
				"objectId": embedId,
				"objectType": embedType,
				"link": embedLink,
				"title": embedTitle,
				"content": embedContent,
				"mediaList": embedImage
			},
			"extensions": {"mentionedArray": mentions},
		}
		if replyTo: data["replyMessageId"] = replyTo
		if stickerId:
			data["content"] = None
			data["stickerId"] = stickerId
			data["type"] = MessageTypes.Sticker

		if file:
			data["content"] = None
			fileType = guess_type(file.name)[0]
			if fileType == UploadType.audio:
				data["type"] = MessageTypes.Voice
				data["mediaType"] = 110
			elif fileType in (UploadType.image_png, UploadType.image_jpg):
				data["mediaType"] = 100
				data["mediaUploadValueContentType"] = fileType
				data["mediaUhqEnabled"] = True
			elif fileType == UploadType.gif:
				data["mediaType"] = 100
				data["mediaUploadValueContentType"] = fileType
				data["mediaUhqEnabled"] = True
			else: raise WrongType("file type not allowed.")
			data["mediaUploadValue"] = b64encode(file.read()).decode()
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/message", data)

	def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str = None) -> DynamicObject:
		if asStaff:
			data = {
				"adminOpName": 102,
			}
			if reason:data["adminOpNote"] = {"content": reason}
			return self.req.request("POST", f"/g/s/chat/thread/{chatId}/message/{messageId}/admin", data)
		else:return self.req.request("DELETE", f"/g/s/chat/thread/{chatId}/message/{messageId}", data)


	def mark_as_read(self, chatId: str, messageId: str) -> DynamicObject:
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/mark-as-read", {
			"messageId": messageId,
		})

	def send_coins(self, coins: int, blogId: str = None, chatId: str = None, objectId: str = None, transactionId: str = None):

		if transactionId is None:
			transactionId = str(uuid4())

		data = {
			"coins": coins,
			"tippingContext": {"transactionId": transactionId if transactionId else str(uuid4())},
		}

		if blogId is not None:
			url = f"/g/s/blog/{blogId}/tipping"
		elif chatId is not None:
			url = f"/g/s/chat/thread/{chatId}/tipping"
		elif objectId is not None:
			data["objectId"] = objectId
			data["objectType"] = 2
			url = f"/g/s/tipping"
		else:raise SpecifyType

		response = self.session.post(url, json=data)
		return self.req.request("POST", url, data=data)

	def follow(self, userId: Union[str, list]):
		if isinstance(userId, str):
			return self.req.request("POST", f"/g/s/user-profile/{userId}/member")
		elif isinstance(userId, list):
			data = {"targetUidList": userId}
			return self.req.request("POST", f"/g/s/user-profile/{self.profile.userId}/joined", data=data)
		else: raise WrongType

	def unfollow(self, userId: str):
		return self.req.request("DELETE", f"/g/s/user-profile/{userId}/member/{self.profile.userId}")

	def block(self, userId: str):
		return self.req.request("POST", f"/g/s/block/{userId}")
	
	def unblock(self, userId: str):
		return self.req.request("DELETE", f"/g/s/block/{userId}")

	def join_community(self, comId: int, invitationId: str = None):
		
		data = {}
		if invitationId:data["invitationId"] = invitationId
		return self.req.request("POST", f"/x{comId}/s/community/join", data=data)

	def request_join_community(self, comId: int, message: str = None):
		return self.req.request("POST", f"/x{comId}/s/community/membership-request", data={"message": message})

	def leave_community(self, comId: int):
		return self.req.request("POST", f"/x{comId}/s/community/leave")

	def flag_community(self, comId: int, reason: str, flagType: int, isGuest: bool = False):

		data = {
			"objectId": comId,
			"objectType": 16,
			"flagType": flagType,
			"message": reason,
		}
		return self.req.request("POST", f"/x{comId}/s/{'g-flag' if isGuest else 'flag'}", data=data)


	def edit_profile(self, nickname: str = None, content: str = None, icon: BinaryIO = None, backgroundColor: str = None, backgroundImage: str = None, defaultBubbleId: str = None):

		data = {
			"address": None,
			"latitude": 0,
			"longitude": 0,
			"mediaList": None,
			"eventSource": "UserProfileView",
		}

		if nickname:
			data["nickname"] = nickname
		if icon:
			data["icon"] = self.req.upload_media(icon).mediaValue
		if content:
			data["content"] = content
		if backgroundColor:
			data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if backgroundImage:
			data["extensions"] = {"style": {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}}
		if defaultBubbleId:
			data["extensions"] = {"defaultBubbleId": defaultBubbleId}
	
		return self.req.request("POST", f"/g/s/user-profile/{self.profile.userId}", data=data)


	def set_amino_id(self, aminoId: str):
		return self.req.request("POST", f"/g/s/account/change-amino-id", data={"aminoId": aminoId})

	def get_linked_communities(self, userId: str):
		return self.req.request("GET", f"/g/s/user-profile/{userId}/linked-community")["linkedCommunityList"]

	def get_unlinked_communities(self, userId: str):
		return self.req.request("GET", f"/g/s/user-profile/{userId}/linked-community")["unlinkedCommunityList"]

	def reorder_linked_communities(self, comIds: list):
		return self.req.request("POST", f"/g/s/user-profile/{self.profile.userId}/linked-community/reorder", data={"ndcIds": comIds})

	def add_linked_community(self, comId: int):
		return self.req.request("POST", f"/g/s/user-profile/{self.profile.userId}/linked-community/{comId}")

	def remove_linked_community(self, comId: int):
		return self.req.request("DELETE", f"/g/s/user-profile/{self.profile.userId}/linked-community/{comId}")
	

	def comment(self, message: str, userId: str = None, blogId: str = None, wikiId: str = None, replyTo: str = None, stickerId: str = None):

		data = {
			"content": message,
			"stickerId": None,
			"type": 0,
		}


		if stickerId:
			data["content"] = None
			data["stickerId"] = stickerId
			data["type"] = 3
		if replyTo:
			data["respondTo"] = replyTo
		if userId:
			data["eventSource"] = "UserProfileView"
			url = f"/g/s/user-profile/{userId}/g-comment"
		elif blogId:
			data["eventSource"] = "PostDetailView"
			url = f"/g/s/blog/{blogId}/g-comment"
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/g/s/item/{wikiId}/g-comment"
		else: raise SpecifyType

		return self.req.request("POST", url, data=data)


	def delete_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):

		if userId:url = f"/g/s/user-profile/{userId}/g-comment/{commentId}"
		elif blogId:url = f"/g/s/blog/{blogId}/g-comment/{commentId}"
		elif wikiId:url = f"/g/s/item/{wikiId}/g-comment/{commentId}"
		else:raise SpecifyType

		return self.req.request("DELETE", url)

	def like_blog(self, blogId: Union[str, list] = None, wikiId: str = None):

		data = {
			"value": 4,
		}

		if blogId:
			if isinstance(blogId, str):
				data["eventSource"] = "UserProfileView"
				url = f"/g/s/blog/{blogId}/g-vote?cv=1.2"
			elif isinstance(blogId, list):
				data["targetIdList"] = blogId
				url = f"/g/s/feed/g-vote"
			else: raise WrongType(type(blogId))
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/g/s/item/{wikiId}/g-vote?cv=1.2"
		else: raise SpecifyType
		
		return self.req.request("POST", url, data=data)
	

	def unlike_blog(self, blogId: str = None, wikiId: str = None):
		
		if blogId:url = f"/g/s/blog/{blogId}/g-vote?eventSource=UserProfileView"
		elif wikiId:url = f"/g/s/item/{wikiId}/g-vote?eventSource=PostDetailView"
		else:raise SpecifyType

		return self.req.request("DELETE", url)

	def like_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
		
		data = {
			"value": 4,
		}
		if userId:
			data["eventSource"] = "UserProfileView"
			url = f"/g/s/user-profile/{userId}/comment/{commentId}/g-vote?cv=1.2&value=1"
		elif blogId:
			data["eventSource"] = "PostDetailView"
			url = f"/g/s/blog/{blogId}/comment/{commentId}/g-vote?cv=1.2&value=1"
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/g/s/item/{wikiId}/comment/{commentId}/g-vote?cv=1.2&value=1"
		else: raise SpecifyType

		return self.req.request("POST", url, data=data)

	def unlike_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
		if userId:url = f"/g/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView"
		elif blogId:url = f"/g/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		elif wikiId:url = f"/g/s/item/{wikiId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		else:raise SpecifyType
		
		return self.req.request("DELETE", url)


	def get_membership_info(self):
		return self.req.request("GET", f"/g/s/membership?force=true")

	def get_ta_announcements(self, language: str = "en", start: int = 0, size: int = 25):
		if language not in self.get_supported_languages():raise UnsupportedLanguage(language)
		return self.req.request("GET", f"/g/s/announcement?language={language}&start={start}&size={size}")["blogList"]

	def get_wallet_info(self):
		return self.req.request("GET", f"/g/s/wallet")["wallet"]


	def get_wallet_history(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/g/s/wallet/coin/history?start={start}&size={size}")["coinHistoryList"]

	def get_from_deviceid(self, deviceId: str):
		return self.req.request("GET", f"/g/s/auid?deviceId={deviceId}")["auid"]


	def get_from_link(self, link: str):
		return self.req.request("GET", f"/g/s/link-resolution?q={link}")["linkInfoV2"]


	def get_from_id(self, objectId: str, objectType: int, comId: int = None):
		data = {
			"objectId": objectId,
			"targetCode": 1,
			"objectType": objectType,
		}

		return self.req.request("POST", f"/g/{f's-x{comId}' if comId else 's'}/link-resolution", data=data)["linkInfoV2"]


	def get_supported_languages(self):
		return self.req.request("GET", f"/g/s/community-collection/supported-languages?start=0&size=100")["supportedLanguages"]


	def claim_coupon(self) -> DynamicObject:
		return self.req.request("GET", f"/g/s/coupon/new-user-coupon/claim")
	

	def get_subscriptions(self, start: int = 0, size: int = 25) -> list:
		return self.req.request("GET", f"/g/s/store/subscription?objectType=122&start={start}&size={size}")["storeSubscriptionItemList"]

	def get_all_users(self, start: int = 0, size: int = 25) -> DynamicObject:
		return self.req.request("GET", f"/g/s/user-profile?type=recent&start={start}&size={size}")
	


	def transfer_host(self, chatId: str, userIds: list) -> DynamicObject:
		data = {
			"uidList": userIds,
		}

		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/transfer-organizer", data=data)
	

	def accept_host(self, chatId: str, requestId: str) -> DynamicObject:
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept")

	def delete_co_host(self, chatId: str, userId: str) -> DynamicObject:
		return self.req.request("DELETE", f"/g/s/chat/thread/{chatId}/co-host/{userId}")



	def link_identify(self, link: str):
		return self.req.request("GET", f"/g/s/community/link-identify?q=http%3A%2F%2Faminoapps.com%2Finvite%2F{link}")


	def invite_to_vc(self, chatId: str, userId: str):
		data = {
			"uid": userId,
		}

		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/vvchat-presenter/invite", data=data)


	def wallet_config(self, level: int):
		data = {
			"adsLevel": level,
		}
	
		return self.req.request("POST", f"/g/s/wallet/ads/config", data=data)


	def purchase(self, objectId: str, isAutoRenew: bool = False):
		data = {
			"objectId": objectId,
			"objectType": 114,
			"v": 1,
			"paymentContext":
			{
				"discountStatus": 0,
				"isAutoRenew": isAutoRenew
			},
		}

		return self.req.request("POST", f"/g/s/store/purchase", data=data)

	def get_public_communities(self, language: str = "en", size: int = 25):
		return self.req.request("GET", f"/g/s/topic/0/feed/community?language=language&type=web-explore&categoryKey=recommendation&size=size&pagingType=t")["communityList"]

	def get_blockers(self) -> list[str]:
		return self.req.request("GET", f"/g/s/block/full-list")["blockerUidList"]
	
	def set_privacy_status(self, isAnonymous: bool = False, getNotifications: bool = False):
		data = {"privacyMode": 2 if isAnonymous else 1}
		if not getNotifications:data["notificationStatus"] = 2
		else:data["privacyMode"] = 1

		return self.req.request("POST", f"/g/s/account/visit-settings", data)
	


	def edit_chat(self, chatId: str, title: str = None, icon: str = None, content: str = None, announcement: str = None, keywords: list = None, pinAnnouncement: bool = None, publishToGlobal: bool = None, fansOnly: bool = None):
		data = {}

		if title:
			data["title"] = title
		if content:
			data["content"] = content
		if icon:
			data["icon"] = icon
		if keywords:
			data["keywords"] = keywords
		if announcement:
			data["extensions"] = {"announcement": announcement}
		if pinAnnouncement:
			data["extensions"] = {"pinAnnouncement": pinAnnouncement}
		if fansOnly:
			data["extensions"] = {"fansOnly": fansOnly}
		if publishToGlobal is not None:
			data["publishToGlobal"] = 0 if publishToGlobal is True else 1

		return self.req.request("POST", f"/g/s/chat/thread/{chatId}", data)



	def do_not_disturb(self, chatId: str, doNotDisturb: bool = True) -> DynamicObject:
		data = {
			"alertOption": 2 if doNotDisturb else 1,
		}
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/member/{self.userId}/alert", data)




	def pin_chat(self, chatId: str, pin: bool = True) -> DynamicObject:
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/{'pin' if pin else 'unpin'}", {})


	def set_chat_background(self, chatId: str, backgroundImage: BinaryIO) -> DynamicObject:
		data = {
			"media": [100, self.req.upload_media(backgroundImage).mediaValue, None]
		}
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/member/{self.userId}/background", data)
	
	def add_co_hosts(self, chatId: str, coHosts: list) -> DynamicObject:
		data = {
			"uidList": coHosts
		}
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/co-host", data)

	def chat_view_only(self, chatId: str, viewOnly: bool = False) -> DynamicObject:
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/view-only/{'enable' if viewOnly else 'disable'}")
	
	def member_can_invite_to_chat(self, chatId: str, canInvite: bool = True) -> DynamicObject:
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/members-can-invite/{'enable' if canInvite else 'disable'}")

	def member_can_chat_tip(self, chatId: str, canTip: bool = True) -> DynamicObject:
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/tipping-perm-status/{'enable' if canTip else 'disable'}")
