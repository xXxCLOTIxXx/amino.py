from __future__ import annotations

from .objects.auth_data import auth_data
from .helpers.requests_builder import requestsBuilder
from .helpers.generator import generate_deviceId, sid_to_uid, timezone
from .helpers.exceptions import SpecifyType, WrongType, UnsupportedLanguage
from .ws.socket import Socket

from .objects.args import (
	Gender, UploadType, Sorting, 
	MessageTypes, PurchaseTypes,
	ClientTypes
)

from time import time
from typing import BinaryIO
from base64 import b64encode
from uuid import uuid4
from mimetypes import guess_type


class Client(Socket):
	"""
		Class for working with amino global functions [https://aminoapps.com/]
		Arguments for the class:

		
		- deviceId: str = None
			-  Device ID. Is generated automatically, but you can specify your own
			- amino.generate_deviceId()

		- language: str = "en"
			- The language in which amino servers will respond.
		
		- user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2"
			- device user agent that will see the amino server
		
		- proxies: dict = None
			- dictionary with proxy
		
		- socket_enable: bool = True
			- whether the socket will be launched when logging into your account
			- the socket is used to receive new messages in chats
		
		- sock_trace: bool = False
			- Monitor socket connection

		- sock_debug: bool = False
			- output debug messages in the socket class to the console

		- auto_device: bool = False
			- generate new deviceId every request?

		- auto_user_agent: bool = False
			- generate new user agent every request?

		- timeout: int | None = None
			- waiting time before request is reset
	"""
	
	req: requestsBuilder
	socket_enable = False

	def __init__(self,
			  deviceId: str | None = None,
			  language: str = "en",
			  user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2",
			  proxies: dict | None = None,
			  socket_enable: bool = True,
			  sock_trace: bool = False,
			  sock_debug: bool = False,
			  auto_device: bool = False,
			  auto_user_agent: bool = False,
			  timeout: int | None = None
			  ):

		self.req = requestsBuilder(
			proxies=proxies,
			timeout=timeout,
			profile=auth_data(
				deviceId=deviceId,
				language=language,
				user_agent=user_agent,
				auto_device=auto_device,
				auto_user_agent=auto_user_agent
			)
		)
		self.socket_enable = socket_enable
		Socket.__init__(self, sock_trace, sock_debug)


	def __repr__(self):
		return repr(f"class Client <sid={self.sid}, userId={self.userId}, deviceId={self.deviceId}, user_agent={self.profile.user_agent}, language={self.language}>")

	
	@property
	def profile(self) -> auth_data:
		return self.req.profile
	
	@property
	def userId(self) -> str:
		return self.req.profile.uid

	@property
	def sid(self) -> str:
		return self.req.profile.sid

	@property
	def deviceId(self) -> str:
		return self.req.profile.deviceId
	

	@property
	def language(self) -> str:
		return self.req.profile.language

	@property
	def user_agent(self) -> str:
		return self.req.profile.user_agent



	def login(self, email: str, password: str | None = None, secret: str | None = None, client_type: int = ClientTypes.User):
		"""
		Login into an account.

		**Parameters**
		- email : Email of the account.
		- password : Password of the account.
		- secret : secret of the account
		- client_type: Type of Client.
		"""
		if password is None and secret is None: raise SpecifyType
		result = self.req.request("POST", "/g/s/auth/login", {
			"email": email,
			"v": 2,
			"secret": secret if secret else f"0 {password}",
			"deviceID": self.deviceId,
			"clientType": client_type,
			"action": "normal",
		})
		self.req.profile.sid, self.req.profile.uid = result["sid"], result["auid"]
		if self.socket_enable:
			final = f"{self.deviceId}|{int(time() * 1000)}"
			self.ws_connect(final=final, headers=self.ws_headers(self.sid, final, self.deviceId))
		return result["userProfile"]


	def login_phone(self, phone: str, password: str | None = None, secret: str | None = None, client_type: int = ClientTypes.User):
		"""
		Login into an account.

		**Parameters**
		- phone : phone number of the account.
		- password : Password of the account.
		- client_type: Type of Client.
		"""
		if password is None and secret is None: raise SpecifyType
		result = self.req.request("POST", "/g/s/auth/login", {
			"phoneNumber": phone,
			"v": 2,
			"secret": secret if secret else f"0 {password}",
			"deviceID": self.deviceId,
			"clientType": client_type,
			"action": "normal",
		})
		
		self.req.profile.sid, self.req.profile.uid = result["sid"], result["auid"]
		if self.socket_enable:
			final = f"{self.deviceId}|{int(time() * 1000)}"
			self.ws_connect(final=final, headers=self.ws_headers(self.sid, final, self.deviceId))
		return result["userProfile"]

	
	def login_sid(self, sid: str) -> auth_data:
		"""
		Login into an account.

		**Parameters**
		- sid : auth sid
		"""
		self.req.profile.sid, self.req.profile.uid = sid, sid_to_uid(sid)
		if self.socket_enable:
			final = f"{self.deviceId}|{int(time() * 1000)}"
			self.ws_connect(final=final, headers=self.ws_headers(self.sid, final, self.deviceId))
		return self.profile



	def logout(self):
		"""
		Logout from an account.
		"""
		result = self.req.request("POST", "/g/s/auth/logout", {
			"deviceID": self.profile.deviceId,
			"clientType": 100,
		})
		self.req.profile.sid, self.req.profile.uid = None, None
		if self.socket_enable:self.ws_disconnect()
		return result

	def restore_account(self, email: str, password: str):
		"""
		Restore a deleted account.

		**Parameters**
		- email : Email of the account.
		- password : Password of the account.
		"""
		return self.req.request("POST", "/g/s/account/delete-request/cancel", {
			"secret": f"0 {password}",
			"deviceID": self.deviceId,
			"email": email,
		})
	
	def configure_profile(self, age: int, gender: int = Gender.non_binary):
		"""
		Configure the settings of an account.

		**Parameters**
		- age : Age of the account. Minimum is 13.
		- gender : Gender of the account.
			- ``Gender.male``, ``Gender.female`` or ``Gender.non_binary``
		"""
		if gender not in Gender.all:raise SpecifyType
		return self.req.request("POST", "/g/s/persona/profile/basic", {
			"age": max(13, age),
			"gender": gender,
		})	


	def activity_status(self, status: bool):
		"""
		Sets your activity status to offline or online.

		**Parameters**
		- status: bool
			- True: online
			- False: offline
		"""

		if status not in (True, False): raise WrongType(status)
		return self.req.request("POST", f"/g/s/user-profile/{self.userId}/online-status", {
			"onlineStatus": 1 if status is True else 2,
			"duration": 86400,
		})



	def verify_account(self, email: str, code: str):
		"""
		Verify an account.

		**Parameters**
		- email : Email of the account.
		- code : Verification code.
		"""
		return self.req.request("POST", "/g/s/auth/check-security-validation", {
			"validationContext": {
				"type": 1,
				"identity": email,
				"data": {"code": code}},
			"deviceID": self.deviceId,
		})


	def request_verify_code(self, email: str, resetPassword: bool = False):
		"""
		Request an verification code to the targeted email.

		**Parameters**
		- email : Email of the account.
		- resetPassword : If the code should be for Password Reset.
		"""

		data = {
			"identity": email,
			"type": 1,
			"deviceID": self.deviceId,
		}
		if resetPassword is True:
			data["level"] = 2
			data["purpose"] = "reset-password"
		return self.req.request("POST", "/g/s/auth/request-security-validation", data)

	def activate_account(self, email: str, code: str):
		"""
		Activate an account.

		**Parameters**
		- email : Email of the account.
		- code : Verification code.
		"""
		
		return self.req.request("POST", "/g/s/auth/activate-email", {
			"type": 1,
			"identity": email,
			"data": {"code": code},
			"deviceID": self.deviceId,
		})


	def delete_account(self, password: str):
		"""
		Delete an account.

		**Parameters**
		- password: Password of the account.
		"""
		return self.req.request("POST", "/g/s/account/delete-request", {
			"deviceID": self.deviceId,
			"secret": f"0 {password}",
		})


	def change_password(self, email: str, password: str, code: str):
		"""
		Change password of an account.

		**Parameters**
		- email : Email of the account.
		- code : Verification code.
		- old_password : old password of account.
		- new_password : new password for account.

		"""
		
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

	#from amino.fixfix
	#worked?
	def change_email(self, password: str, old_email: str, old_code: str, new_email: str, new_code: str):
		"""
		Change email of an account.

		**Parameters**
		- password : Password from account.
		- old_email : Old email of the account.
		- old_code : Verification code from old email.
		- new_email : New email for account.
		- new_code : Verification code from new email.
		"""

		data = {
			"secret": f"0 {password}",
			"deviceTokenType": 0,
			"clientType": 100,
			"systemPushEnabled": 1,
			"newValidationContext": {
				"identity": new_email,
				"data": {
					"code": str(new_code)
				},
				"deviceID": self.deviceId,
				"type": 1,
				"level": 1
			},
			"locale": "en_BY",
			"level": 1,
			"oldValidationContext": {
				"identity": old_email,
				"data": {
					"code": str(old_code)
				},
				"deviceID": self.deviceId,
				"type": 1,
				"level": 1
			},
			"bundleID": "com.narvii.master",
			"timezone": timezone(),
			"deviceID": self.deviceId,
			"clientCallbackURL": "narviiapp://default"
		}

		return self.req.request("POST", f"/g/s/auth/update-email", data=data)




	def check_device(self, deviceId: str, locale: str = "en_US"):
		"""
		Check if the Device ID is valid.

		**Parameters**
		- deviceId : ID of the Device.
		- locale : Locale like "ru_RU", "en_US"
		"""
		data = {
			"deviceID": deviceId,
			"bundleID": "com.narvii.amino.master",
			"clientType": 100,
			"timezone": timezone(),
			"systemPushEnabled": True,
			"locale": locale,
		}

		return self.req.request("POST", f"/g/s/device", data=data)



	def get_eventlog(self):
		"""
		Get eventlog
		"""
		return self.req.request("GET", f"/g/s/eventlog/profile?language={self.language}")



	def get_account_info(self):
		"""
		Getting account info about you.
		"""
		return self.req.request("GET", "/g/s/account")["account"]


	def my_communities(self, start: int = 0, size: int = 25):
		"""
		List of Communities the account is in.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/g/s/community/joined?v=1&start={start}&size={size}")["communityList"]


	def profiles_in_communities(self, start: int = 0, size: int = 25):
		"""
		Getting your profiles in communities.

		**Parameters**:
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/g/s/community/joined?v=1&start={start}&size={size}")["userInfoInCommunities"]


	def get_user_info(self, userId: str):
		"""
		Information of an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.request("GET", f"/g/s/user-profile/{userId}")["userProfile"]

	def get_my_chats(self, start: int = 0, size: int = 25):
		"""
		List of Chats the account is in.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.

		"""
		return self.req.request("GET", f"/g/s/chat/thread?type=joined-me&start={start}&size={size}")["threadList"]

	def get_chat(self, chatId: str):
		"""
		Get the Chat Object from an Chat ID.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return self.req.request("GET", f"/g/s/chat/thread/{chatId}")["thread"]

	def get_chat_users(self, chatId: str, start: int = 0, size: int = 25):
		"""
		Getting users in chat.

		**Parameters**:
		- chatId : ID of the Chat.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/g/s/chat/thread/{chatId}/member?cv=1.2&type=default&start={start}&size={size}")["memberList"]

	def join_chat(self, chatId: str):
		"""
		Join an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/member/{self.userId}")

	def leave_chat(self, chatId: str):
		"""
		Leave an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return self.req.request("DELETE", f"/g/s/chat/thread/{chatId}/member/{self.userId}")

	def start_chat(self, userId: str | list | tuple, message: str, title: str | None = None, content: str | None = None, isGlobal: bool = False, publishToGlobal: bool = False):
		"""
		Start an Chat with an User or List of Users.

		**Parameters**
		- userId : ID of the User or List of User IDs.
		- message : Starting Message.
		- title : Title of Group Chat.
		- content : Content of Group Chat.
		- isGlobal : If Group Chat is Global.
		- publishToGlobal : If Group Chat should show in Global.
		"""
		if isinstance(userId, (str, list, tuple)):
			userIds = list(userId) if isinstance(userId, str) else userId
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

	def invite_to_chat(self, userId: str | list, chatId: str):
		"""
		Invite a User or List of Users to a Chat.

		**Parameters**
		- userId : ID of the User or List of User IDs.
		- chatId : ID of the Chat.

		"""
		if not isinstance(userId, (str, list)):raise WrongType(type(userId))
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/member/invite", {
			"uids": list(userId) if isinstance(userId, str) else userId,
		})


	def kick(self, userId: str, chatId: str, allowRejoin: bool = True):
		"""
		Kick/ban user from/in chat.

		Parameters:
		- userId: ID of the User or List of User IDs.
		- chatId: ID of the Chat.
		- allowRejoin: bool = True
			- if False, it will ban user in chat
		"""
		return self.req.request("DELETE", f"/g/s/chat/thread/{chatId}/member/{userId}?allowRejoin={int(allowRejoin)}")

	def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str | None = None):
		"""
		List of Messages from an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		- size : Size of the list.
		- pageToken : Next Page Token.
		"""
		return self.req.request("GET", f"/g/s/chat/thread/{chatId}/message?pagingType=t&size={size}{f'&pageToken={pageToken}' if pageToken else ''}")

	def get_message_info(self, chatId: str, messageId: str):
		"""
		Information of an Message from an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		- messageId : ID of the Message.

		"""
		return self.req.request("GET", f"/g/s/chat/thread/{chatId}/message/{messageId}")["message"]

	def get_community_info(self, comId: int):
		"""
		Information of an Community.

		**Parameters**
		- comId : ID of the Community.
		"""
		return self.req.request("GET", f"/g/s-x{comId}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount")["community"]

	def search_community(self, aminoId: str):
		"""
		Search a Community by Amino ID.

		**Parameters**
		- aminoId : Amino ID of the Community.
		"""
		return self.req.request("GET", f"/g/s/search/amino-id-and-link?q={aminoId}")["resultList"]

	def get_user_following(self, userId: str, start: int = 0, size: int = 25):
		"""
		List of Users that the User is Following.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/g/s/user-profile/{userId}/joined?start={start}&size={size}")["userProfileList"]

	def get_user_followers(self, userId: str, start: int = 0, size: int = 25):
		"""
		List of Users that are Following the User.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/g/s/user-profile/{userId}/member?start={start}&size={size}")["userProfileList"]


	def get_user_visitors(self, userId: str, start: int = 0, size: int = 25):
		"""
		List of Users that Visited the User.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/g/s/user-profile/{userId}/visitors?start={start}&size={size}")


	def visit(self, userId: str):
		"""
		Visit an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.request("GET", f"/g/s/user-profile/{userId}?action=visit")


	def get_blocked_users(self, start: int = 0, size: int = 25):
		"""
		List of Users that the User Blocked.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/g/s/block?start={start}&size={size}")["userProfileList"]

	def get_blocker_users(self, start: int = 0, size: int = 25):
		"""
		Get a list of users who have blocked you

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/g/s/block/full-list?start={start}&size={size}")["blockerUidList"]
	
	def get_blog_info(self, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None):
		"""
		Getting blog info.

		**Parameters**:
		- blogId: Id of the blog
		- wikiId:  Id of the wiki
		- quizId:  Id of the quiz
		- fileId:  Id of the file
			- if all fields are None, exception will be raised
			- if more than one field not empty, it will return only one object using priority like this:
				- quizId -> blogId -> wikiId -> fileId
		"""
		if blogId or quizId:
			return self.req.request("GET", f"/g/s/blog/{quizId if quizId is not None else blogId}")
		if wikiId:
			return self.req.request("GET", f"/g/s/item/{wikiId}")
		if fileId:
			return self.req.request("GET", f"/g/s/shared-folder/files/{fileId}")["file"]
		raise SpecifyType()


	def get_blog_comments(self, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None, sorting: str = Sorting.Newest, start: int = 0, size: int = 25):
		"""
		Getting blog info.

		**Parameters**:
		- start : Where to start the list.
		- size : Size of the list.
		- sorting: Type of sorting of received objects
		- blogId: Id of the blog
		- wikiId:  Id of the wiki
		- quizId:  Id of the quiz
		- fileId:  Id of the file
			- if all fields are None, exception will be raised
			- if more than one field not empty, it will return only one object using priority like this:
				- blogId -> quizId -> wikiId -> fileId
		"""
		if sorting not in Sorting.all:raise WrongType(sorting)
		if blogId or quizId:url = f"/g/s/blog/{quizId if not blogId else blogId}/comment"
		elif wikiId:url = f"/g/s/item/{wikiId}/comment"
		elif fileId:url = f"/g/s/shared-folder/files/{fileId}/comment"
		else:raise SpecifyType
		return self.req.request("GET", f"{url}?sort={sorting}&start={start}&size={size}")["commentList"]

	def get_wall_comments(self, userId: str, sorting: str = Sorting.Newest, start: int = 0, size: int = 25):
		"""
		List of Wall Comments of an User.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		- sorting: Type of sorting of received objects
		"""
		if sorting not in Sorting.all:raise WrongType(sorting)
		return self.req.request("GET", f"/g/s/user-profile/{userId}/g-comment?sort={sorting}&start={start}&size={size}")["commentList"]

	def flag(self, reason: str, flagType: int, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None, asGuest: bool = False):
		"""
		Flag a User, Blog or Wiki.

		**Parameters**
		- reason : Reason of the Flag.
		- flagType : Type of the Flag.
		- userId : ID of the User.
		- blogId : ID of the Blog.
		- wikiId : ID of the Wiki.
		- asGuest : Execute as a Guest.
		"""
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




	def send_message(self, chatId: str, message: str | None = None, messageType: int = MessageTypes.Text, file: BinaryIO | None = None, replyTo: str | None = None, mentionUserIds: list | None = None, stickerId: str | None = None, embedId: str | None = None, embedType: int | None = None, embedLink: str | None = None, embedTitle: str | None = None, embedContent: str | None = None, embedImage: BinaryIO | None = None):
		"""
		Send a Message to a Chat.

		**Parameters**
		- message : Message to be sent
		- chatId : ID of the Chat.
		- file : File to be sent.
		- messageType : Type of the Message.
		- mentionUserIds : List of User IDS to mention. '@' needed in the Message.
		- replyTo : Message ID to reply to.
		- stickerId : Sticker ID to be sent.
		- embedType : Type of the Embed. Can be aminofixfix.lib.objects.EmbedTypes only. By default it's LinkSnippet one.
		- embedLink : Link of the Embed. Can be only "ndc://" link if its AttachedObject.
		- embedImage : Image of the Embed. Required to send Embed, if its LinkSnippet. Can be only 1024x1024 max. Can be string to existing image uploaded to Amino or it can be opened (not readed) file.
		- embedId : ID of the Embed. Works only in AttachedObject Embeds. It can be any ID, just gen it using str_uuid4().
		- embedType : Type of the AttachedObject Embed. Works only in AttachedObject Embeds. Just look what values AttachedObjectTypes enum contains.
		- embedTitle : Title of the Embed. Works only in AttachedObject Embeds. Can be empty.
		- embedContent : Content of the Embed. Works only in AttachedObject Embeds. Can be empty.
		"""
		
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

	def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str | None = None):
		"""
		Delete a Message from a Chat.

		**Parameters**
		- messageId : ID of the Message.
		- chatId : ID of the Chat.
		- asStaff : If execute as a Staff member (Leader or Curator).
		- reason : Reason of the action to show on the Moderation History.
		"""
		if asStaff:
			data = {
				"adminOpName": 102,
			}
			if reason:data["adminOpNote"] = {"content": reason}
			return self.req.request("POST", f"/g/s/chat/thread/{chatId}/message/{messageId}/admin", data)
		else:return self.req.request("DELETE", f"/g/s/chat/thread/{chatId}/message/{messageId}", data)


	def mark_as_read(self, chatId: str, messageId: str):
		"""
		Mark a Message from a Chat as Read.

		**Parameters**
		- messageId : ID of the Message.
		- chatId : ID of the Chat.
		"""
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/mark-as-read", {
			"messageId": messageId,
		})

	def send_coins(self, coins: int, blogId: str | None = None, chatId: str | None = None, objectId: str | None = None, transactionId: str | None = None):
		"""
		Sending coins.

		**Parameters**
		- coins : number of coins to send (maximum 500 at a time)
		- blogId : ID of the Blog.
		- chatId : ID of the Chat.
		- objectId : ID of some object.
		- transactionId : transaction ID (automatically generated by default)
		"""
		
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

		return self.req.request("POST", url, data=data)

	def follow(self, userId: str | list):
		"""
		Follow an User or Multiple Users.

		**Parameters**
		- userId : ID of the User or List of IDs of the Users.
		"""
		if isinstance(userId, str):
			return self.req.request("POST", f"/g/s/user-profile/{userId}/member")
		elif isinstance(userId, list):
			data = {"targetUidList": userId}
			return self.req.request("POST", f"/g/s/user-profile/{self.profile.userId}/joined", data=data)
		else: raise WrongType

	def unfollow(self, userId: str):
		"""
		Unfollow an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.request("DELETE", f"/g/s/user-profile/{userId}/member/{self.profile.userId}")

	def block(self, userId: str):
		"""
		Block an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.request("POST", f"/g/s/block/{userId}")
	
	def unblock(self, userId: str):
		"""
		Unblock an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.request("DELETE", f"/g/s/block/{userId}")

	def join_community(self, comId: int, invitationId: str | None = None):
		"""
		Join a Community.

		**Parameters**
		- comId : ID of the Community.
		- invitationId : ID of the Invitation Code.
		"""
		
		data = {}
		if invitationId:data["invitationId"] = invitationId
		return self.req.request("POST", f"/x{comId}/s/community/join", data=data)

	def request_join_community(self, comId: int, message: str = None):
		"""
		Request to join a Community.

		**Parameters**
		- comId : ID of the Community.
		- message : Message to be sent.
		"""
		return self.req.request("POST", f"/x{comId}/s/community/membership-request", data={"message": message})

	def leave_community(self, comId: int):
		"""
		Leave a Community.

		**Parameters**
		- comId : ID of the Community.
		"""
		return self.req.request("POST", f"/x{comId}/s/community/leave")

	def flag_community(self, comId: int, reason: str, flagType: int, isGuest: bool = False):
		"""
		Flag a Community.

		**Parameters**
		- comId : ID of the Community.
		- reason : Reason of the Flag.
		- flagType : Type of Flag.
		"""
		data = {
			"objectId": comId,
			"objectType": 16,
			"flagType": flagType,
			"message": reason,
		}
		return self.req.request("POST", f"/x{comId}/s/{'g-flag' if isGuest else 'flag'}", data=data)


	def edit_profile(self, nickname: str | None = None, content: str | None = None, icon: BinaryIO | None = None, backgroundColor: str | None = None, backgroundImage: str | None = None, defaultBubbleId: str | None = None):
		"""
		Edit account's Profile.

		**Parameters**
		- nickname : Nickname of the Profile.
		- content : Biography of the Profile.
		- icon : Icon of the Profile.
		- backgroundImage : Url of the Background Picture of the Profile.
		- backgroundColor : Hexadecimal Background Color of the Profile.
		- defaultBubbleId : Chat bubble ID.
		
		"""
		
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


	def set_privacy_status(self, isAnonymous: bool | None = False, getNotifications: bool | None = False):
		"""
		Edit account's Privacy Status.

		**Parameters**
		- isAnonymous : If visibility should be Anonymous or not.
		- getNotifications : If account should get new Visitors Notifications.
		"""

		data = {}

		if isAnonymous is not None:
			if isAnonymous is False: data["privacyMode"] = 1
			if isAnonymous is True: data["privacyMode"] = 2
		if getNotifications:
			if getNotifications is False: data["notificationStatus"] = 2
			if getNotifications is True: data["privacyMode"] = 1
		if not data:raise SpecifyType("Specify arguments.")

		return self.req.request("POST", f"/g/s/account/visit-settings", data=data)


	def set_amino_id(self, aminoId: str):
		"""
		Edit account's Amino ID.

		**Parameters**
			- aminoId : Amino ID of the Account.
		"""
		return self.req.request("POST", f"/g/s/account/change-amino-id", data={"aminoId": aminoId})

	def get_linked_communities(self, userId: str):
		"""
		Get a List of Linked Communities of an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.request("GET", f"/g/s/user-profile/{userId}/linked-community")["linkedCommunityList"]

	def get_unlinked_communities(self, userId: str):
		"""
		Get a List of Unlinked Communities of an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.request("GET", f"/g/s/user-profile/{userId}/linked-community")["unlinkedCommunityList"]

	def reorder_linked_communities(self, comIds: list):
		"""
		Reorder List of Linked Communities.

		**Parameters**
		- comIds : IDS of the Communities.
		"""
		return self.req.request("POST", f"/g/s/user-profile/{self.profile.userId}/linked-community/reorder", data={"ndcIds": comIds})

	def add_linked_community(self, comId: int):
		"""
		Add a Linked Community on your profile.

		**Parameters**
			- comId : ID of the Community.
		"""
		return self.req.request("POST", f"/g/s/user-profile/{self.profile.userId}/linked-community/{comId}")

	def remove_linked_community(self, comId: int):
		"""
		Remove a Linked Community on your profile.

		**Parameters**
		- comId : ID of the Community.
		"""
		return self.req.request("DELETE", f"/g/s/user-profile/{self.profile.userId}/linked-community/{comId}")
	

	def comment(self, message: str, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None, replyTo: str | None = None, stickerId: str | None = None):
		"""
		Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- message : Message to be sent.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		- replyTo : ID of the Comment to Reply to.
		- stickerId: ID of the sticker
		"""
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


	def delete_comment(self, commentId: str, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None):
		"""
		Delete a Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- commentId : ID of the Comment.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
		if userId:url = f"/g/s/user-profile/{userId}/g-comment/{commentId}"
		elif blogId:url = f"/g/s/blog/{blogId}/g-comment/{commentId}"
		elif wikiId:url = f"/g/s/item/{wikiId}/g-comment/{commentId}"
		else:raise SpecifyType

		return self.req.request("DELETE", url)

	def like_blog(self, blogId: str | list = None, wikiId: str = None):
		"""
		Like a Blog, Multiple Blogs or a Wiki.

		**Parameters**
		- blogId : ID of the Blog or List of IDs of the Blogs. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""

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
	

	def unlike_blog(self, blogId: str | None = None, wikiId: str | None = None):
		"""
		Remove a like from a Blog or Wiki.

		**Parameters**
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
		
		if blogId:url = f"/g/s/blog/{blogId}/g-vote?eventSource=UserProfileView"
		elif wikiId:url = f"/g/s/item/{wikiId}/g-vote?eventSource=PostDetailView"
		else:raise SpecifyType

		return self.req.request("DELETE", url)

	def like_comment(self, commentId: str, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None):
		"""
		Like a Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- commentId : ID of the Comment.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
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

	def unlike_comment(self, commentId: str, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None):
		"""
		Remove a like from a Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- commentId : ID of the Comment.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
		if userId:url = f"/g/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView"
		elif blogId:url = f"/g/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		elif wikiId:url = f"/g/s/item/{wikiId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		else:raise SpecifyType
		
		return self.req.request("DELETE", url)


	def get_membership_info(self):
		"""
		Get Information about your Amino+ Membership.
		"""
		return self.req.request("GET", f"/g/s/membership?force=true")

	def get_ta_announcements(self, language: str = "en", start: int = 0, size: int = 25):
		"""
		Get the list of Team Amino's Announcement Blogs.

		**Parameters**
		- language : Language of the Blogs.
			- ``client.get_supported_languages()``
			- ``en``, ``es``, ``ru``, ``fr``, ...
		- start : Where to start the list.
		- size : Size of the list.
		"""
		if language not in self.get_supported_languages():raise UnsupportedLanguage(language)
		return self.req.request("GET", f"/g/s/announcement?language={language}&start={start}&size={size}")["blogList"]

	def get_wallet_info(self):
		"""
		Get Information about the account's Wallet.
		"""
		return self.req.request("GET", f"/g/s/wallet")["wallet"]


	def get_wallet_history(self, start: int = 0, size: int = 25):
		"""
		Get the Wallet's History Information.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/g/s/wallet/coin/history?start={start}&size={size}")["coinHistoryList"]

	def get_from_deviceid(self, deviceId: str):
		"""
		Get the User ID from an Device ID.

		**Parameters**
		- deviceID : ID of the Device.
		"""
		return self.req.request("GET", f"/g/s/auid?deviceId={deviceId}")["auid"]


	def get_from_link(self, link: str):
		"""
		Get the Object Information from the Amino URL.

		**Parameters**
		- link : link from the Amino.
			- ``http://aminoapps.com/p/EXAMPLE``, the ``link`` is 'EXAMPLE'.
		"""
		return self.req.request("GET", f"/g/s/link-resolution?q={link}")["linkInfoV2"]


	def get_from_id(self, objectId: str, objectType: int, comId: int | None = None):
		"""
		Get the Object Information from the Object ID and Type.

		**Parameters**
		- objectID : ID of the Object. User ID, Blog ID, etc.
		- objectType : Type of the Object.
		- comId : ID of the Community. Use if the Object is in a Community.
		"""
		data = {
			"objectId": objectId,
			"targetCode": 1,
			"objectType": objectType,
		}

		return self.req.request("POST", f"/g/{f's-x{comId}' if comId else 's'}/link-resolution", data=data)["linkInfoV2"]


	def get_supported_languages(self):
		"""
		Get the List of Supported Languages by Amino.
		"""
		return self.req.request("GET", f"/g/s/community-collection/supported-languages?start=0&size=100")["supportedLanguages"]


	def claim_coupon(self):
		"""
		Claim the New User Coupon available when a new account is created.
		"""
		return self.req.request("GET", f"/g/s/coupon/new-user-coupon/claim")
	

	def get_subscriptions(self, start: int = 0, size: int = 25) -> list:
		"""
		Get Information about the account's Subscriptions.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/g/s/store/subscription?objectType=122&start={start}&size={size}")["storeSubscriptionItemList"]

	def get_all_users(self, start: int = 0, size: int = 25):
		"""
		Get list of users of Amino.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/g/s/user-profile?type=recent&start={start}&size={size}")
	


	def transfer_host(self, chatId: str, userIds: list[str]):
		"""
		transfer host from chat

		**Parameters**:
		- chatId: id of the chat 
		- userIds: id of the user's
		"""
		data = {
			"uidList": userIds,
		}

		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/transfer-organizer", data=data)
	

	def accept_host(self, chatId: str, requestId: str):
		"""
		Accepting host in chat.

		**Parameters**:
		- chatId: id of the chat 
		- requestId: host transfer request ID
		"""
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept")

	def delete_co_host(self, chatId: str, userId: str):
		"""
		Remove co-host from chat
		**Parameters**:
		- chatId: id of the chat 
		- userId: id of the user 
		"""
		return self.req.request("DELETE", f"/g/s/chat/thread/{chatId}/co-host/{userId}")



	def link_identify(self, code: str):
		"""
		Getting info about invite from code. 

		**Parameters**:
		- code: str
			- *code* is thing *after* http://aminoapps.com/invite/
		"""
		return self.req.request("GET", f"/g/s/community/link-identify?q=http%3A%2F%2Faminoapps.com%2Finvite%2F{code}")


	def invite_to_vc(self, chatId: str, userId: str):
		"""
		Invite a User to a Voice Chat

		**Parameters**
		- chatId : ID of the Chat
		- userId : ID of the User
		"""
		data = {
			"uid": userId,
		}

		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/vvchat-presenter/invite", data=data)


	def wallet_config(self, level: int):
		"""
		Changes ads config

		**Parameters**
		- level - Level of the ads.
			- ``1``, ``2``
		"""
		
		data = {
			"adsLevel": level,
		}
	
		return self.req.request("POST", f"/g/s/wallet/ads/config", data=data)


	def purchase(self, objectId: str, objectType: int = PurchaseTypes.Bubble, isAutoRenew: bool = False):
		"""
		Purchasing something from store

		**Parameters**:
		- objectId: id of object that you wanna buy
		- isAutoRenew: do you wanna auto renew your purchase?
		"""
		data = {
			"objectId": objectId,
			"objectType": objectType,
			"v": 1,
			"paymentContext":
			{
				"discountStatus": 0,
				"isAutoRenew": isAutoRenew
			},
		}

		return self.req.request("POST", f"/g/s/store/purchase", data=data)

	def get_public_communities(self, language: str = "en", size: int = 25):
		"""
		Get public communites

		**Parameters**
		- language : Set up language
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/g/s/topic/0/feed/community?language={language}&type=web-explore&categoryKey=recommendation&size={size}&pagingType=t")["communityList"]


	def edit_chat(self, chatId: str, title: str | None = None, icon: str | None = None, content: str | None = None, announcement: str | None = None, keywords: list | None = None, pinAnnouncement: bool | None = None, publishToGlobal: bool | None = None, fansOnly: bool | None = None):
		"""
		edit chat settings

		**Parameters**
		- chatId : id of the chat
		- title : set chat title
		- icon : set chat icon
		- content : set chat description
		- announcement : Announcement of the Chat
		- keywords : List of Keywords of the Chat
		- pinAnnouncement : If the Chat Announcement should Pinned or not
		- publishToGlobal : If the Chat should show on Public Chats or not.
		- fansOnly : If the Chat should be Fans Only or not.
		"""

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



	def do_not_disturb(self, chatId: str, doNotDisturb: bool = True):
		"""
		change chat notifications

		**Parameters**
		- chatId : id of the chat
		- doNotDisturb : If the Chat should Do Not Disturb or not.
		"""
		data = {
			"alertOption": 2 if doNotDisturb else 1,
		}
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/member/{self.userId}/alert", data)




	def pin_chat(self, chatId: str, pin: bool = True):
		"""
		Pin chat

		**Parameters**
		- chatId : id of the chat
		- pin : If the Chat should Pinned or not.
		"""
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/{'pin' if pin else 'unpin'}", {})


	def set_chat_background(self, chatId: str, backgroundImage: BinaryIO):
		"""
		Change chat background

		**Parameters**
		- chatId : id of the chat
		- backgroundImage : picture for background
		"""

		data = {
			"media": [100, self.req.upload_media(backgroundImage).mediaValue, None]
		}
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/member/{self.userId}/background", data)
	
	def add_co_hosts(self, chatId: str, coHosts: list):
		"""
		Add assistants to chat

		**Parameters**
		- chatId : id of the chat
		- coHosts : user id's
		"""

		data = {
			"uidList": coHosts
		}
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/co-host", data)

	def chat_view_only(self, chatId: str, viewOnly: bool = False):
		"""
		set view-only mode

		**Parameters**
		- chatId : id of the chat
		- viewOnly : enable view only mode?
		"""
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/view-only/{'enable' if viewOnly else 'disable'}")
	
	def member_can_invite_to_chat(self, chatId: str, canInvite: bool = True):
		"""
		permission to invite users to chat

		**Parameters**
		- chatId : id of the chat
		- canInvite : member can invite to chat ?.
		"""
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/members-can-invite/{'enable' if canInvite else 'disable'}")

	def member_can_chat_tip(self, chatId: str, canTip: bool = True):
		"""
		permission to tip chat

		**Parameters**
		- chatId : id of the chat
		- canTip : if the Chat should be Tippable or not.
		"""
		return self.req.request("POST", f"/g/s/chat/thread/{chatId}/tipping-perm-status/{'enable' if canTip else 'disable'}")