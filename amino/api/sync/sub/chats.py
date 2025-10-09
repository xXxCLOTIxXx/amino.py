from amino.api.base import BaseClass
from amino import args, MediaObject
from amino.helpers.generator import clientrefid, b64encode, get_iso_timestamp
from amino import WrongType
from amino import (Chat, Message, BaseObject, ChatMessages, UserProfile)

from typing import BinaryIO
from mimetypes import guess_type
from uuid import uuid4

class CommunityChatsModule(BaseClass):
	comId: str | int | None
	def upload_media(self, file: BinaryIO, fileType: str | None = None) -> MediaObject: ...


	def start_public_chat(self, title: str, icon: BinaryIO, content: str = "", userId: str | list | tuple = [], publishToGlobal: bool = False, comId: str | int | None = None) -> Chat:
		if isinstance(userId, str): userId = [userId]
		data = {
			"title": title,
			"content": content,
			"type": args.ChatTypes.Public,
			"publishToGlobal": 1 if publishToGlobal is True else 0,
			"eventSource": "GlobalComposeMenu",
			"inviteeUids": userId,
			"uid": self.userId,
			"icon": self.upload_media(icon).mediaValue
		}

		return Chat(self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/chat/thread", data).json())

	def start_private_chat(self, userId: str, message: str | None = None, comId: str | int | None = None) -> Chat:

		data = {
			"type": args.ChatTypes.Private,
			"inviteeUids": [userId],
			"uid": self.userId,
		}
		if message:data["initialMessageContent"] = message

		return Chat(self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/chat/thread", data).json())

	def start_group_chat(self, userIds: list | tuple, message: str | None = None, comId: str | int | None = None) -> Chat:

		data = {
			"type": args.ChatTypes.Group,
			"inviteeUids": userIds,
			"uid": self.userId,
		}
		if message:data["initialMessageContent"] = message

		return Chat(self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/chat/thread", data).json())

	def invite_to_chat(self, userId: str | list | tuple, chatId: str, comId: str | int | None = None) -> BaseObject:
		"""
		Invite a User or List of Users to a Chat.

		**Parameters**
		- userId : ID of the User or List of User IDs.
		- chatId : ID of the Chat.
		"""
		if isinstance(userId, str): userIds = [userId]
		elif isinstance(userId, list): userIds = userId
		elif isinstance(userId, tuple): userIds = userId
		else: raise WrongType(f"userId: {type(userId)}")
		data = { "uids": userIds, "uid": self.userId}

		return BaseObject(self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/chat/thread/{chatId}/member/invite", data).json())

	def send_message(self, chatId: str, message: str, replyId: str | None = None, mentionUserIds: list | None = None, comId: str | int | None = None) -> Message:
		
		message = message.replace("<@", "‎‏").replace("@>", "‬‭")

		data = {
		"type": args.MessageTypes.Text,
		"content": message,
		#"clientRefId": clientrefid(),
		"attachedObject": None,
		"uid": self.userId
		}

		if replyId:data["replyMessageId"] = replyId
		if mentionUserIds:
			mentions = [{"uid": mention_uid} for mention_uid in mentionUserIds]
			data["extensions"] = {"mentionedArray": mentions}

		return Message(self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/chat/thread/{chatId}/message", data).json())

	def send_sticker(self, chatId: str, stickerId: str, comId: str | int | None = None) -> Message:

		data = {
		"type": args.MessageTypes.Sticker,
		#"clientRefId": clientrefid(),
		"uid": self.userId,
		"stickerId": stickerId
		}

		return Message(self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/chat/thread/{chatId}/message", data).json())

	def send_media(self, chatId: str, file: BinaryIO, fileType: str | None = None, mediaUhqEnabled: bool = False, comId: str | int | None = None) -> Message:
		
		if fileType is None:
			fileType = guess_type(file.name)[0]

		data = {
			"type": args.MessageTypes.Text,
			"content": None,
			"clientRefId": clientrefid(),
			"attachedObject": None,
			"mediaUploadValueContentType": fileType,
			"uid": "a8bfbad0-4427-4999-bb08-b0b65092b869"
			}


		data["mediaUploadValue"] = b64encode(file.read()).decode()
		if fileType == args.UploadType.audio:
			#TODO FIX
			data["type"] =  args.MessageTypes.Voice
			data["mediaType"] = 110
		elif fileType in [
			args.UploadType.gif,
			args.UploadType.image_jpeg,
			args.UploadType.image_jpg,
			args.UploadType.image_png]:
			data["mediaUhqEnabled"] = mediaUhqEnabled
			data["mediaType"] = 100

		return Message(self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/chat/thread/{chatId}/message", data).json())

	def send_video(self, chatId: str, videoFile: BinaryIO, imageFile: BinaryIO, message: str | None = None, mediaUhqEnabled: bool = False, comId: str | int | None = None) -> Message:
		#TODO FIX
		"""
		Sending video.

		**Parameters**
		- chatId: chat Id
		- message: message
		- videoFile: BinaryIO open(file, "rb") (video file)
		- imageFile: BinaryIO open(file, "rb") (image file)
		"""

		i =  str(uuid4()).upper()
		cover = f"{i}_thumb.jpg"
		video = f"{i}.mp4"
		
		data = {
			"clientRefId": clientrefid(),
			"content": message,
			"mediaType": 123,
			"videoUpload":
			{
				"contentType": "video/mp4",
				"cover": cover,
				"video": video
			},
			"type": args.MessageTypes.Video,
			"mediaUhqEnabled": mediaUhqEnabled,
			"extensions": {},
			"uid": self.userId 
		}

		files = {
			video: (video, videoFile.read(), 'video/mp4'),
			cover: (cover, imageFile.read(), 'application/octet-stream'),
			'payload': (None, data, 'application/octet-stream')
		}
		return Message(self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/chat/thread/{chatId}/message", data, files=files, content_type=None).json())

	def send_link_snippet(self, chatId: str, link: str, image: BinaryIO, message: str, comId: str | int | None = None) -> Message:
		#TODO FIX
		
		"""
		send full embed
		**Parameters**
		- message : Message to be sent
		- chatId : ID of the Chat.
		- link : Link of the Embed. Can be only "ndc://" link
		- image : Image of the Embed. Required to send Embed, Can be only 1024x1024 max. Can be string to existing image uploaded to Amino or it can be opened (not readed) file.
		"""

		fileType = guess_type(image.name)[0]

		data = {
			"type": args.MessageTypes.Text,
			"content": message,
			"clientRefId": clientrefid(),
			"attachedObject": None,
			"extensions": {
				"linkSnippetList": [{
					"link": link,
					"mediaUploadValueContentType": fileType,
					"mediaType": 100,
					"mediaUploadValue": b64encode(image.read()).decode()
				}]
			},
			"uid": self.userId
		}

		return Message(self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/chat/thread/{chatId}/message", data).json())

	def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str | None = None, comId: str | int | None = None) -> BaseObject:
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
			return BaseObject(self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/chat/thread/{chatId}/message/{messageId}/admin", data).json())
		return BaseObject(self.req.make_sync_request("DELETE",  f"/x{comId or self.comId}/s/chat/thread/{chatId}/message/{messageId}").json())

	def mark_as_read(self, chatId: str, messageId: str, comId: str | int | None = None) -> BaseObject:
		"""
		Mark a Message from a Chat as Read.

		**Parameters**
		- messageId : ID of the Message.
		- chatId : ID of the Chat.
		"""
		data = {
			"messageId": messageId,
			"uid": self.userId,
			"createdTime": get_iso_timestamp()
			}
		return BaseObject(self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/chat/thread/{chatId}/mark-as-read", data).json())

	def edit_chat(self, chatId: str, title: str | None = None, icon: BinaryIO | None = None, backgroundImage: BinaryIO | None = None, content: str | None = None, announcement: str | None = None, keywords: list | None = None, pinAnnouncement: bool | None = None, publishToGlobal: bool | None = None, fansOnly: bool | None = None, comId: str | int | None = None) -> BaseObject:
		"""
		Edit chat settings.

		**Parameters**
		- chatId : ID of the Chat.
		- title : Title of the Chat.
		- content : Content of the Chat.
		- icon : Icon of the Chat.
		- backgroundImage: background Image of chat
		- announcement : Announcement of the Chat.
		- pinAnnouncement : If the Chat Announcement should Pinned or not.
		- keywords : List of Keywords of the Chat.
		- publishToGlobal** : If the Chat should show on Public Chats or not.
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

		return BaseObject(self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/chat/thread/{chatId}", data).json())

	def do_not_disturb(self, chatId: str, doNotDisturb: bool = True, comId: str | int | None = None) -> BaseObject:
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
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}/member/{self.userId}/alert", data).json())

	def pin_chat(self, chatId: str, pin: bool = True, comId: str | int | None = None) -> BaseObject:
		"""
		Pin chat

		**Parameters**
		- chatId : id of the chat
		- pin : If the Chat should Pinned or not.
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}{'pin' if pin else 'unpin'}", {}).json())

	def add_co_hosts(self, chatId: str, coHosts: list, comId: str | int | None = None) -> BaseObject:
		"""
		Add assistants to chat

		**Parameters**
		- chatId : id of the chat
		- coHosts : user id's
		"""
		data = {
			"uidList": coHosts
		}
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}/co-host", data).json())

	def delete_co_host(self, chatId: str, userId: str, comId: str | int | None = None) -> BaseObject:
		"""
		Remove co-host from chat
		**Parameters**:
		- chatId: id of the chat 
		- userId: id of the user 
		"""
		return BaseObject(self.req.make_sync_request("DELETE", f"/x{comId or self.comId}/chat/thread/{chatId}/co-host/{userId}").json())

	def chat_view_only(self, chatId: str, viewOnly: bool = False, comId: str | int | None = None) -> BaseObject:
		"""
		set view-only mode

		**Parameters**
		- chatId : id of the chat
		- viewOnly : enable view only mode?
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}/view-only/{'enable' if viewOnly else 'disable'}").json())
	
	def member_can_invite_to_chat(self, chatId: str, canInvite: bool = True, comId: str | int | None = None) -> BaseObject:
		"""
		permission to invite users to chat

		**Parameters**
		- chatId : id of the chat
		- canInvite : member can invite to chat ?.
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}/members-can-invite/{'enable' if canInvite else 'disable'}").json())

	def member_can_chat_tip(self, chatId: str, canTip: bool = True, comId: str | int | None = None) -> BaseObject:
		"""
		permission to tip chat

		**Parameters**
		- chatId : id of the chat
		- canTip : if the Chat should be Tippable or not.
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}/tipping-perm-status/{'enable' if canTip else 'disable'}").json())

	def transfer_host(self, chatId: str, userIds: list[str], comId: str | int | None = None) -> BaseObject:
		"""
		transfer host from chat

		**Parameters**:
		- chatId: id of the chat 
		- userIds: id of the user's
		"""
		data = { "uid": userIds }
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}/transfer-organizer", data).json())

	def accept_host(self, chatId: str, requestId: str, comId: str | int | None = None) -> BaseObject:
		"""
		Accepting host in chat.

		**Parameters**:
		- chatId: id of the chat 
		- requestId: host transfer request ID
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept").json())

	def kick(self, userId: str, chatId: str, allowRejoin: bool = True, comId: str | int | None = None) -> BaseObject:
		return BaseObject(self.req.make_sync_request("DELETE", f"/x{comId or self.comId}/s/chat/thread/{chatId}/member/{userId}?allowRejoin={int(allowRejoin)}").json())

	def join_chat(self, chatId: str, comId: str | int | None = None) -> BaseObject:
		"""
		Join an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}/member/{self.userId}", content_type="application/x-www-form-urlencoded").json())

	def leave_chat(self, chatId: str, comId: str | int | None = None) -> BaseObject:
		"""
		Leave an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return BaseObject(self.req.make_sync_request("DELETE", f"/x{comId or self.comId}/s/chat/thread/{chatId}/member/{self.userId}", content_type="application/x-www-form-urlencoded").json())

	def delete_chat(self, chatId: str, comId: str | int | None = None) -> BaseObject:
		"""
		Delete a Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return BaseObject(self.req.make_sync_request("DELETE", f"/x{comId or self.comId}/s/chat/thread/{chatId}").json())

	def vc_permission(self, chatId: str, permission: int = args.VoiceChatJoinPermissions.Open, comId: str | int | None = None) -> BaseObject:
		"""
		Manage permissions to VC.

		**Parameters**
		- chatId: chat ID
		- permission: voice chat access (use ``amino.arguments.VoiceChatJoinPermissions. some``)
		"""
		data = { "vvChatJoinType": permission }
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}/vvchat-permission", data).json())

	def get_vc_reputation_info(self, chatId: str, comId: str | int | None = None) -> BaseObject:
		"""
		Get info about reputation that you got from VC.

		**Parameters**
		- chatId: chat ID
		"""
		return BaseObject(self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/chat/thread/{chatId}/avchat-reputation").json())

	def claim_vc_reputation(self, chatId: str, comId: str | int | None = None) -> BaseObject:
		"""
		Claim reputation that you got from VC.

		**Parameters**
		- chatId: chat ID
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}/avchat-reputation").json())


	def get_my_chats(self, start: int = 0, size: int = 25, comId: str | int | None = None) -> list[Chat]:
		"""
		List of Chats the account is in.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		result = self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/chat/thread?type=joined-me&start={start}&size={size}").json()["threadList"]
		return [Chat(x) for x in result]


	def get_public_chats(self, type: str = args.Sorting2.Recommended, start: int = 0, size: int = 25, comId: str | int | None = None) -> list[Chat]:
		"""
		List of Public Chats of the Community.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		- type : filter chats by type. use ``Sorting2`` object
		"""
		result = self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/chat/thread?type=public-all&filterType={type}&start={start}&size={size}").json()["threadList"]
		return [Chat(x) for x in result]

	def get_chat(self, chatId: str, comId: str | int | None = None) -> Chat:
		"""
		Get the Chat Object from an Chat ID.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return Chat(self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/chat/thread/{chatId}").json())

	def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str | None = None, comId: str | int | None = None) -> ChatMessages:
		"""
		List of Messages from an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		- size : Size of the list.
		- pageToken : Next Page Token.
		"""
		return ChatMessages(self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}{f'&pageToken={pageToken}' if pageToken else  ''}").json())

	def get_message_info(self, chatId: str, messageId: str, comId: str | int | None = None) -> Message:
		"""
		Information of an Message from an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		- message : ID of the Message.
		"""
		return Message(self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/chat/thread/{chatId}/message/{messageId}").json())



	def get_chat_users(self, chatId: str, start: int = 0, size: int = 25, comId: str | int | None = None) -> list[UserProfile]:
		"""
		Getting users in chat.

		**Parameters**
		- chatId: chat id
		- start: int
			- start pos
		- size: int
			- how much you want to get
		"""
		result = self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/chat/thread/{chatId}/member?type=default&cv=1.2&start={start}&size={size}").json()["memberList"]
		return [UserProfile(x) for x in result]


	def invite_to_vc(self, chatId: str, userId: str, comId: str | int | None = None) -> BaseObject:
		"""
		Invite a User to a Voice Chat

		**Parameters**
		- chatId - ID of the Chat
		- userId - ID of the User
		"""
		data = { "uid": userId }
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}/vvchat-presenter/invite/", data).json())
