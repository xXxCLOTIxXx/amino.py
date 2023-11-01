
from .models.objects import profile
from .helpers import exceptions
from .client import Client
from .helpers.generators import timezone

from json import dumps
import base64

from uuid import UUID
from os import urandom
from typing import BinaryIO, Union
from binascii import hexlify
from time import time as timestamp
from json_minify import json_minify
from base64 import b64encode

class CommunityClient(Client):
	def __init__(self, comId: int = None, community_link: str = None, aminoId: str = None, profile: profile = None, language: str = "en", user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2", deviceId: str = None, auto_device: bool = False, socket_enabled: bool = True, socket_debug: bool = False, socket_trace: bool = False, socket_whitelist_communities: list = None, socket_old_message_mode: bool = False, proxies: dict = None, certificate_path = None):
		Client.__init__(self, language=language, user_agent=user_agent, deviceId=deviceId, auto_device=auto_device, socket_enabled=socket_enabled, socket_debug=socket_debug, socket_trace=socket_trace, socket_whitelist_communities=socket_whitelist_communities, socket_old_message_mode=socket_old_message_mode, proxies=proxies, certificate_path=certificate_path)
		if profile:self.profile=profile

		if comId:
			self.comId=comId
		elif community_link:
			self.comId=self.get_from_link(community_link).comId
		elif aminoId:
			self.comId=self.get_from_link(f"http://aminoapps.com/c/{aminoId}").comId
		else:
			raise exceptions.NoCommunity("Provide a link to the community, comId or aminoId.")


#ACCOUNT=============================


	def check_in(self, tz: int = None) -> int:
		data = dumps({
			"timezone": tz if tz else timezone(),
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/check-in", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def repair_check_in(self, method: int = 1) -> int:
		#1 Coins
		#2 Amino+

		data = dumps({
			"timestamp": int(timestamp() * 1000),
			"repairMethod": str(method)
		})
		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/check-in/repair", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def lottery(self, tz: int = None) -> dict:
		data = dumps({
			"timezone": tz if tz else timezone(),
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/check-in/lottery", data=data, headers=self.get_headers(data=data))
		return response.json()["lotteryLog"]



	def edit_profile(self, nickname: str = None, content: str = None, icon: BinaryIO = None, chatRequestPrivilege: str = None, imageList: list = None, backgroundImage: str = None, backgroundColor: str = None, titles: list = None, defaultBubbleId: str = None) -> int:
		
		mediaList = list()
		data = {"timestamp": int(timestamp() * 1000)}

		if imageList is not None:
			for image, caption  in imageList:
				mediaList.append([100, self.upload_media(image, "image"), caption])
			data["mediaList"] = mediaList


		if nickname: data["nickname"] = nickname
		if icon: data["icon"] = self.upload_media(icon, "image")
		if content: data["content"] = content
		if chatRequestPrivilege: data["extensions"] = {"privilegeOfChatInviteRequest": chatRequestPrivilege}
		if backgroundImage: data["extensions"] = {"style": {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}}
		if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if defaultBubbleId: data["extensions"] = {"defaultBubbleId": defaultBubbleId}

		if titles:
			_titles = list
			for titles, colors in titles:
				_titles.append({"title": titles, "color": colors})
			data["extensions"] = {"customTitles": _titles}
		data = dumps(data)

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-profile/{self.profile.userId}", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def check_notifications(self) -> int:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/notification/checked", headers=self.get_headers())
		return response.status_code


	def delete_notification(self, notificationId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/notification/{notificationId}", headers=self.get_headers())
		return response.status_code


	def clear_notifications(self) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/notification", headers=self.get_headers())
		return response.status_code


	def get_notifications(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/notification?pagingType=t&start={start}&size={size}", headers=self.get_headers())
		return response.json()["notificationList"]


	def get_notices(self, start: int = 0, size: int = 25):


		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/notice?type=usersV2&status=1&start={start}&size={size}", headers=self.get_headers())
		return response.json()["noticeList"]


	def send_active_obj(self, startTime: int = None, endTime: int = None, optInAdsFlags: int = 2147483647, tz: int = None, timers: list = None, timestamp: int = int(timestamp() * 1000)) -> int: 
		data = {"userActiveTimeChunkList": [{"start": startTime, "end": endTime}], "timestamp": timestamp, "optInAdsFlags": optInAdsFlags, "timezone": tz if tz else timezone()} 
		if timers: data["userActiveTimeChunkList"] = timers 
		data = json_minify(dumps(data))  

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/community/stats/user-active-time", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def online_status(self, status: str) -> int:

		if status.lower() not in ("on", "off"): raise exceptions.WrongType(status)
		data = dumps({
			"onlineStatus": 1 if status.lower() == "on" else 2,
			"duration": 86400,
			"timestamp": int(timestamp() * 1000)
		})
	
		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/user-profile/{self.profile.userId}/online-status", data=data, headers=self.get_headers(data=data))
		return response.status_code

#COINS=============================

	def send_coins(self, coins: int, blogId: str = None, chatId: str = None, objectId: str = None, transactionId: str = None) -> int:

		if transactionId is None: transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))


		data = {
			"coins": coins,
			"tippingContext": {"transactionId": transactionId},
			"timestamp": int(timestamp() * 1000)
		}

		if blogId is not None: url = f"/x{self.comId}/s/blog/{blogId}/tipping"
		elif chatId is not None: url = f"/x{self.comId}/s/chat/thread/{chatId}/tipping"
		elif objectId is not None:
			data["objectId"] = objectId
			data["objectType"] = 2
			url = f"/x{self.comId}/s/tipping"
		else: raise exceptions.SpecifyType()

		data = dumps(data)
		response = self.make_request(method="POST", endpoint=url, data=data, headers=self.get_headers(data=data))
		return response.status_code


	def thank_tip(self, chatId: str, userId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users/{userId}/thank", headers=self.get_headers())
		return response.status_code


	def subscribe(self, userId: str, autoRenew: str = False, transactionId: str = None):
		if transactionId is None: transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))

		data = dumps({
			"paymentContext": {
				"transactionId": transactionId,
				"isAutoRenew": autoRenew
			},
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/influencer/{userId}/subscribe", data=data, headers=self.get_headers(data=data))
		return response.status_code

#USERS=============================

	def get_all_users(self, type: str = "recent", start: int = 0, size: int = 25) -> dict:

		if type.lower() not in ("recent", "banned", "featured", "leaders", "curators"):raise exceptions.WrongType(type)
		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile?type={type.lower()}&start={start}&size={size}", headers=self.get_headers())
		return response.json()


	def get_online_users(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/live-layer?topic=ndtopic:x{self.comId}:online-members&start={start}&size={size}", headers=self.get_headers())
		return response.json()


	def get_online_favorite_users(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-group/quick-access?type=online&start={start}&size={size}", headers=self.get_headers())
		return response.json()


	def get_user_info(self, userId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}", headers=self.get_headers())
		return response.json()["userProfile"]


	def get_user_following(self, userId: str, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}/joined?start={start}&size={size}", headers=self.get_headers())
		return response.json()["userProfileList"]

	def get_user_followers(self, userId: str, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}/member?start={start}&size={size}", headers=self.get_headers())
		return response.json()["userProfileList"]

	def get_user_visitors(self, userId: str, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/s/user-profile/{userId}/visitors?start={start}&size={size}", headers=self.get_headers())
		return response.json()


	def get_user_checkins(self, userId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/check-in/stats/{userId}?timezone={timezone()}", headers=self.get_headers())
		return response.json()


	def get_user_achievements(self, userId: str):
	
		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}/achievements", headers=self.get_headers())
		return response.json()["achievements"]


	def get_influencer_fans(self, userId: str, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}/achievements", headers=self.get_headers())
		return response.json()


	def add_to_favorites(self, userId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-group/quick-access/{userId}", headers=self.get_headers())
		return response.status_code

	def follow(self, userId: Union[str, list]) -> int:

		if isinstance(userId, str):
			response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-profile/{userId}/member", headers=self.get_headers())
		elif isinstance(userId, list):
			data = dumps({"targetUidList": userId, "timestamp": int(timestamp() * 1000)})
			response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-profile/{self.profile.userId}/joined", data=data, headers=self.get_headers(data=data))
		else: raise exceptions.WrongType(userId)
		return response.status_code

	def unfollow(self, userId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/user-profile/{self.profile.userId}/joined/{userId}", headers=self.get_headers())
		return response.status_code


	def block(self, userId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/block/{userId}", headers=self.get_headers())
		return response.status_code


	def unblock(self, userId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/block/{userId}", headers=self.get_headers())
		return response.status_code


	def visit(self, userId: str) -> int:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}?action=visit", headers=self.get_headers())
		return response.status_code



	def get_blocked_users(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"{self.api}/x{self.comId}/s/block?start={start}&size={size}", headers=self.get_headers())
		return response.json()["userProfileList"]

	def get_blocker_users(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"{self.api}/x{self.comId}/s/block?start={start}&size={size}", headers=self.get_headers())
		return response.json()["blockerUidList"]


	def search_users(self, nickname: str, start: int = 0, size: int = 25):

		response = self.make_request(method="GET", endpoint=f"{self.api}/s/user-profile?type=name&q={nickname}&start={start}&size={size}", headers=self.get_headers())
		return response.json()["userProfileList"]

	def get_tipped_users(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, chatId: str = None, start: int = 0, size: int = 25):

		if blogId or quizId:part=f"blog/{quizId if quizId else blogId}"
		elif wikiId:part=f"item/{wikiId}"
		elif chatId:part=f"chat/thread/{chatId}"
		elif fileId:part=f"shared-folder/files/{fileId}"
		else: raise exceptions.SpecifyType()

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/{part}/tipping/tipped-users-summary?start={start}&size={size}", headers=self.get_headers())
		return response.json()

	def get_chat_users(self, chatId: str, start: int = 0, size: int = 25):

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2", headers=self.get_headers())
		return response.json()["memberList"]


#CHAT=============================

	def start_chat(self, userId: Union[str, list], message: str, title: str = None, content: str = None, isGlobal: bool = False, publishToGlobal: bool = False) -> dict:

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
		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread", data=data, headers=self.get_headers(data=data))
		return response.json()["thread"]


	def edit_chat(self, chatId: str, doNotDisturb: bool = None, pinChat: bool = None, title: str = None, icon: str = None, backgroundImage: str = None, content: str = None, announcement: str = None, coHosts: list = None, keywords: list = None, pinAnnouncement: bool = None, publishToGlobal: bool = None, canTip: bool = None, viewOnly: bool = None, canInvite: bool = None, fansOnly: bool = None) -> list:
		#TODO
		pass


	def invite_to_chat(self, userId: Union[str, list], chatId: str) -> int:

		if isinstance(userId, str): userIds = [userId]
		elif isinstance(userId, list): userIds = userId
		else: raise exceptions.WrongType(type(userId))

		data = dumps({
			"uids": userIds,
			"timestamp": int(timestamp() * 1000)
		})
		

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/member/invite", data=data, headers=self.get_headers(data=data))
		return response.status_code

	def join_chat(self, chatId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}", headers=self.get_headers(content_type="application/x-www-form-urlencoded"))
		return response.status_code

	def leave_chat(self, chatId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}", headers=self.get_headers())
		return response.status_code

		
	def delete_chat(self, chatId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}", headers=self.get_headers())
		return response.status_code

	def get_chat_threads(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread?type=joined-me&start={start}&size={size}", headers=self.get_headers())
		return response.json()["threadList"]

	def get_public_chat_threads(self, type: str = "recommended", start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/s/chat/thread?type=public-all&filterType={type}&start={start}&size={size}", headers=self.get_headers())
		return response.json()["threadList"]


	def get_chat_thread(self, chatId: str):

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}", headers=self.get_headers())
		return response.json()["thread"]


	def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str = None) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}"+ f"&pageToken={pageToken}" if pageToken else '', headers=self.get_headers())
		return response.json()


	def get_message_info(self, chatId: str, messageId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}", headers=self.get_headers()).json()
		return response["message"]


	def send_message(self, chatId: str, message: str = None, messageType: int = 0, file: BinaryIO = None, fileType: str = None, replyTo: str = None, mentionUserIds: list = None, stickerId: str = None, embedId: str = None, embedType: int = None, embedLink: str = None, embedTitle: str = None, embedContent: str = None, embedImage: BinaryIO = None) -> int:

		if message is not None and file is None and mentionUserIds is not None:
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

			data["mediaUploadValue"] = b64encode(file.read()).decode()

		data = dumps(data)
		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message", data=data, headers=self.get_headers(data=data))
		return response.status_code



	def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str = None) -> int:

		data = {
			"adminOpName": 102,
			"timestamp": int(timestamp() * 1000)
		}
		if asStaff and reason:data["adminOpNote"] = {"content": reason}
		data = dumps(data)

		if not asStaff:response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}", headers=self.get_headers())
		else:response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}/admin", data=data, headers=self.get_headers(data=data))
		return response.status_code



	def send_embed(self, link: str, image: BinaryIO, message: str, chatId: str) -> int:
		data = dumps({
			"type": 0,
			"content": message,
			"extensions": {
				"linkSnippetList": [{
					"link": link,
					"mediaType": 100,
					"mediaUploadValue": b64encode(image.read()).decode(),
					"mediaUploadValueContentType": "image/png"
				}]
			},
				"clientRefId": int(timestamp() / 10 % 100000000),
				"timestamp": int(timestamp() * 1000),
				"attachedObject": None
		})
		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def mark_as_read(self, chatId: str, messageId: str) -> int:

		data = dumps({
			"messageId": messageId,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/mark-as-read", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def transfer_host(self, chatId: str, userIds: list) -> int:
		data = dumps({
			"uidList": userIds,
			"timestamp": int(timestamp() * 1000)
		})


		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer", data=dumps({}), headers=self.get_headers(data=dumps({})))
		return response.status_code


	def accept_host(self, chatId: str, requestId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept", data=dumps({}), headers=self.get_headers(data=dumps({})))
		return response.status_code


	def kick(self, userId: str, chatId: str, allowRejoin: bool = True) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/member/{userId}?allowRejoin={1 if allowRejoin else 0}", headers=self.get_headers())
		return response.status_code



	def invite_to_vc(self, chatId: str, userId: str) -> int:

		data = dumps({"uid": userId})
		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/vvchat-presenter/invite/", data=data, headers=self.get_headers(data=data))
		return response.status_code

	def change_vc_permission(self, chatId: str, permission: int) -> int:

		data = dumps({
			"vvChatJoinType": permission,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/vvchat-permission", headers=self.get_headers())
		return response.status_code


	def get_vc_reputation_info(self, chatId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation", headers=self.get_headers())
		return response.json()

	def claim_vc_reputation(self, chatId: str) -> dict:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation", headers=self.get_headers())
		return response.json()



	def apply_bubble(self, bubbleId: str, chatId: str, applyToAll: bool = False) -> int:
		data = dumps({
			"applyToAll": 1 if applyToAll is True else 0,
			"bubbleId": bubbleId,
			"threadId": chatId,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/apply-bubble", data=data, headers=self.get_headers(data=data))
		return response.json()




#STAFF=============================
	def get_invite_codes(self, status: str = "normal", start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s-x{self.comId}/community/invitation?status={status}&start={start}&size={size}", headers=self.get_headers())
		return response.json()["communityInvitationList"]

	def generate_invite_code(self, duration: int = 0, force: bool = True) -> dict:
		data = dumps({
			"duration": duration,
			"force": force,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/g/s-x{self.comId}/community/invitation", data=data, headers=self.get_headers(data=data))
		return response.json()["communityInvitation"]


	def delete_invite_code(self, inviteId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/g/s-x{self.comId}/community/invitation/{inviteId}", headers=self.get_headers())
		return response.status_code


#OTHER=============================