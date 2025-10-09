from amino.api.base import BaseClass
from amino import WrongType
from amino import args, MediaObject, Message, UserProfile, BaseObject, Chat, ChatMessages
from amino.helpers.generator import clientrefid, b64encode, get_iso_timestamp
from typing import BinaryIO
from mimetypes import guess_type

class GlobalChatsModule(BaseClass):
	

	def upload_media(self, file: BinaryIO, fileType: str | None = None) -> MediaObject: ...

	def get_my_chats(self, start: int = 0, size: int = 25) -> list[Chat]:
		"""
		List of Chats the account is in.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.

		"""
		result = self.req.make_sync_request("GET", f"/g/s/chat/thread?type=joined-me&start={start}&size={size}").json()["threadList"]
		return [Chat(x) for x in result]


	def get_chat(self, chatId: str) -> Chat:
		"""
		Get the Chat Object from an Chat ID.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return Chat(self.req.make_sync_request("GET", f"/g/s/chat/thread/{chatId}").json())

	def get_chat_users(self, chatId: str, start: int = 0, size: int = 25) -> list[UserProfile]:
		"""
		Getting users in chat.

		**Parameters**:
		- chatId : ID of the Chat.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		result = self.req.make_sync_request("GET", f"/g/s/chat/thread/{chatId}/member?cv=1.2&type=default&start={start}&size={size}").json()["memberList"]
		return [UserProfile(x) for x in result]


	def join_chat(self, chatId: str) -> BaseObject:
		"""
		Join an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/member/{self.userId}", content_type="application/x-www-form-urlencoded").json())

	def leave_chat(self, chatId: str) -> BaseObject:
		"""
		Leave an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return BaseObject(self.req.make_sync_request("DELETE", f"/g/s/chat/thread/{chatId}/member/{self.userId}", content_type="application/x-www-form-urlencoded").json())


	def start_private_chat(self, userId: str, message: str | None = None) -> Chat:

		data = {
			"type": args.ChatTypes.Private,
			"inviteeUids": [userId],
			"uid": self.userId,
		}
		if message:data["initialMessageContent"] = message

		return Chat(self.req.make_sync_request("POST",  f"/g/s/chat/thread", data).json())

	def start_group_chat(self, userIds: list | tuple, message: str | None = None) -> Chat:

		data = {
			"type": args.ChatTypes.Group,
			"inviteeUids": userIds,
			"uid": self.userId,
		}
		if message:data["initialMessageContent"] = message

		return Chat(self.req.make_sync_request("POST",  f"/g/s/chat/thread", data).json())


	def invite_to_chat(self, userId: str | list, chatId: str) -> BaseObject:
		"""
		Invite a User or List of Users to a Chat.

		**Parameters**
		- userId : ID of the User or List of User IDs.
		- chatId : ID of the Chat.

		"""
		if not isinstance(userId, (str, list)):raise WrongType(type(userId))
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/member/invite", {
			"uids": list(userId) if isinstance(userId, str) else userId, "uid": self.userId
		}).json())


	def kick(self, userId: str, chatId: str, allowRejoin: bool = True) -> BaseObject:
		"""
		Kick/ban user from/in chat.

		Parameters:
		- userId: ID of the User or List of User IDs.
		- chatId: ID of the Chat.
		- allowRejoin: bool = True
			- if False, it will ban user in chat
		"""
		return BaseObject(self.req.make_sync_request("DELETE", f"/g/s/chat/thread/{chatId}/member/{userId}?allowRejoin={int(allowRejoin)}").json())

	def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str | None = None) -> ChatMessages:
		"""
		List of Messages from an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		- size : Size of the list.
		- pageToken : Next Page Token.
		"""
		return ChatMessages(self.req.make_sync_request("GET", f"/g/s/chat/thread/{chatId}/message?pagingType=t&size={size}{f'&pageToken={pageToken}' if pageToken else ''}").json())

	def get_message_info(self, chatId: str, messageId: str) -> Message:
		"""
		Information of an Message from an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		- messageId : ID of the Message.

		"""
		return Message(self.req.make_sync_request("GET", f"/g/s/chat/thread/{chatId}/message/{messageId}").json())


	def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str | None = None) -> BaseObject:
		"""
		Delete a Message from a Chat.

		**Parameters**
		- messageId : ID of the Message.
		- chatId : ID of the Chat.
		- asStaff : If execute as a Staff member (Leader or Curator).
		- reason : Reason of the action to show on the Moderation History.
		"""
		if asStaff:
			data: dict = {
				"adminOpName": 102,
				"uid": self.userId
			}
			if reason:data["adminOpNote"] = {"content": reason}
			return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/message/{messageId}/admin", data).json())
		else:return BaseObject(self.req.make_sync_request("DELETE", f"/g/s/chat/thread/{chatId}/message/{messageId}").json())


	def mark_as_read(self, chatId: str, messageId: str) -> BaseObject:
		"""
		Mark a Message from a Chat as Read.

		**Parameters**
		- messageId : ID of the Message.
		- chatId : ID of the Chat.
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/mark-as-read", {
			"messageId": messageId,
			"uid": self.userId,
			"createdTime": get_iso_timestamp()
		}).json())


	def transfer_host(self, chatId: str, userIds: list[str]) -> BaseObject:
		"""
		transfer host from chat

		**Parameters**:
		- chatId: id of the chat 
		- userIds: id of the user's
		"""
		data = {
			"uidList": userIds,
		}

		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/transfer-organizer", data).json())
	

	def accept_host(self, chatId: str, requestId: str) -> BaseObject:
		"""
		Accepting host in chat.

		**Parameters**:
		- chatId: id of the chat 
		- requestId: host transfer request ID
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept").json())

	def delete_co_host(self, chatId: str, userId: str) -> BaseObject:
		"""
		Remove co-host from chat
		**Parameters**:
		- chatId: id of the chat 
		- userId: id of the user 
		"""
		return BaseObject(self.req.make_sync_request("DELETE", f"/g/s/chat/thread/{chatId}/co-host/{userId}").json())



	def edit_chat(self, chatId: str, title: str | None = None, icon: BinaryIO | None = None, backgroundImage: BinaryIO | None = None, content: str | None = None, announcement: str | None = None, keywords: list | None = None, pinAnnouncement: bool | None = None, publishToGlobal: bool | None = None, fansOnly: bool | None = None) -> BaseObject:
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


		data: dict = {"uid": self.userId, "extensions":{}}
		
		if title: data["title"] = title
		if content: data["content"] = content
		if icon: data["icon"] = self.upload_media(icon).mediaValue
		if backgroundImage:
			d = [100, self.upload_media(backgroundImage).mediaValue, None]
			data["extensions"]["bm"] = d 
			data["backgroundMedia"] = d
		if keywords: data["keywords"] = keywords
		if announcement: data["extensions"]["announcement"] = announcement
		if pinAnnouncement: data["extensions"]["pinAnnouncement"] = pinAnnouncement
		if fansOnly: data["extensions"]["fansOnly"] = fansOnly
		if publishToGlobal is not None: data["publishToGlobal"] = 0 if publishToGlobal else 1




		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}", data).json())



	def do_not_disturb(self, chatId: str, doNotDisturb: bool = True) -> BaseObject:
		"""
		change chat notifications

		**Parameters**
		- chatId : id of the chat
		- doNotDisturb : If the Chat should Do Not Disturb or not.
		"""
		data = {
			"alertOption": 2 if doNotDisturb else 1,
			"uid": self.userId
		}
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/member/{self.userId}/alert", data).json())




	def pin_chat(self, chatId: str, pin: bool = True) -> BaseObject:
		"""
		Pin chat

		**Parameters**
		- chatId : id of the chat
		- pin : If the Chat should Pinned or not.
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/{'pin' if pin else 'unpin'}", {}).json())


	def set_chat_background(self, chatId: str, backgroundImage: BinaryIO) -> BaseObject:
		"""
		Change chat background

		**Parameters**
		- chatId : id of the chat
		- backgroundImage : picture for background
		"""

		data = {
			"media": [100, self.upload_media(backgroundImage).mediaValue, None]
		}
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/member/{self.userId}/background", data).json())
	
	def add_co_hosts(self, chatId: str, coHosts: list) -> BaseObject:
		"""
		Add assistants to chat

		**Parameters**
		- chatId : id of the chat
		- coHosts : user id's
		"""

		data = {
			"uidList": coHosts
		}
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/co-host", data).json())

	def chat_view_only(self, chatId: str, viewOnly: bool = False) -> BaseObject:
		"""
		set view-only mode

		**Parameters**
		- chatId : id of the chat
		- viewOnly : enable view only mode?
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/view-only/{'enable' if viewOnly else 'disable'}").json())
	
	def member_can_invite_to_chat(self, chatId: str, canInvite: bool = True) -> BaseObject:
		"""
		permission to invite users to chat

		**Parameters**
		- chatId : id of the chat
		- canInvite : member can invite to chat ?.
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/members-can-invite/{'enable' if canInvite else 'disable'}").json())

	def member_can_chat_tip(self, chatId: str, canTip: bool = True) -> BaseObject:
		"""
		permission to tip chat

		**Parameters**
		- chatId : id of the chat
		- canTip : if the Chat should be Tippable or not.
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/tipping-perm-status/{'enable' if canTip else 'disable'}").json())



	def invite_to_vc(self, chatId: str, userId: str) -> BaseObject:
		"""
		Invite a User to a Voice Chat

		**Parameters**
		- chatId : ID of the Chat
		- userId : ID of the User
		"""
		data = {
			"uid": userId,
		}

		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/vvchat-presenter/invite",data).json())
