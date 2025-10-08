from amino.api.base import BaseClass
from amino import WrongType
from amino import args, MediaObject, Message, UserProfile, BaseObject, Chat, ChatMessages
from amino.helpers.generator import clientrefid, b64encode
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
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/member/{self.userId}").json())

	def leave_chat(self, chatId: str) -> BaseObject:
		"""
		Leave an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return BaseObject(self.req.make_sync_request("DELETE", f"/g/s/chat/thread/{chatId}/member/{self.userId}").json())

	def start_chat(self, userId: str | list | tuple, message: str, title: str | None = None, content: str | None = None, isGlobal: bool = False, publishToGlobal: bool = False) -> Chat:
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
		return Chat(self.req.make_sync_request("POST", f"/g/s/chat/thread", data).json()["thread"])

	def invite_to_chat(self, userId: str | list, chatId: str) -> BaseObject:
		"""
		Invite a User or List of Users to a Chat.

		**Parameters**
		- userId : ID of the User or List of User IDs.
		- chatId : ID of the Chat.

		"""
		if not isinstance(userId, (str, list)):raise WrongType(type(userId))
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/member/invite", {
			"uids": list(userId) if isinstance(userId, str) else userId,
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

	def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str | None = None):
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


	def send_message(self, chatId: str, message: str | None = None, messageType: int = args.MessageTypes.Text, file: BinaryIO | None = None, replyTo: str | None = None, mentionUserIds: list | None = None, stickerId: str | None = None, embedId: str | None = None, embedType: int | None = None, embedLink: str | None = None, embedTitle: str | None = None, embedContent: str | None = None, embedImage: BinaryIO | None = None) -> Message:
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
		embedImageList = None
		
		if message is not None:
			message = message.replace("<@", "‎‏").replace("@>", "‬‭")
		mentions = []
		if mentionUserIds:
			for mention_uid in mentionUserIds:
				mentions.append({"uid": mention_uid})
		if embedImage:
			embedImageList = [
			[
				100, self.upload_media(embedImage).mediaValue, None
			]
			]
		data = {
			"type": messageType,
			"content": message,
			"clientRefId": clientrefid(),
			"attachedObject": {
				"objectId": embedId,
				"objectType": embedType,
				"link": embedLink,
				"title": embedTitle,
				"content": embedContent,
				"mediaList": embedImageList
			},
			"extensions": {"mentionedArray": mentions},
		}
		if replyTo: data["replyMessageId"] = replyTo
		if stickerId:
			data["content"] = None
			data["stickerId"] = stickerId
			data["type"] = args.MessageTypes.Sticker

		if file:
			data["content"] = None
			fileType = guess_type(file.name)[0]
			if fileType == args.UploadType.audio:
				data["type"] = args.MessageTypes.Voice
				data["mediaType"] = 110
			elif fileType in (args.UploadType.image_png, args.UploadType.image_jpg):
				data["mediaType"] = 100
				data["mediaUploadValueContentType"] = fileType
				data["mediaUhqEnabled"] = True
			elif fileType == args.UploadType.gif:
				data["mediaType"] = 100
				data["mediaUploadValueContentType"] = fileType
				data["mediaUhqEnabled"] = True
			else: raise WrongType("file type not allowed.")
			data["mediaUploadValue"] = b64encode(file.read()).decode()
		return Message(self.req.make_sync_request("POST", f"/g/s/chat/thread/{chatId}/message", data).json())

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



	def edit_chat(self, chatId: str, title: str | None = None, icon: str | None = None, content: str | None = None, announcement: str | None = None, keywords: list | None = None, pinAnnouncement: bool | None = None, publishToGlobal: bool | None = None, fansOnly: bool | None = None) -> BaseObject:
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
