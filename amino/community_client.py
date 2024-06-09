from .objects.auth_data import auth_data
from .helpers.requests_builder import requestsBuilder
from .helpers.generator import timezone
from .helpers.exceptions import SpecifyType, WrongType

from .objects.args import (
	RepairMethod, CommunityModules, UsersTypes,
	AdministratorsRank, VoiceChatJoinPermissions,
	LeaderboardTypes, Sorting, UploadType, MessageTypes
)
from .objects.dynamic_object import DynamicObject

from typing import Union, BinaryIO
from uuid import uuid4
from base64 import b64encode
from mimetypes import guess_type

class CommunityClient:
	req: requestsBuilder
	comId: str
	
	def __init__(self, profile: auth_data, comId: int, proxies: dict = None):
		self.req = requestsBuilder(proxies=proxies, profile=profile)
		self.comId = comId

	def __repr__(self):
		return repr(f"class CommunityClient <sid={self.sid}, userId={self.userId}, comId={self.comId}, deviceId={self.deviceId}, user_agent={self.profile.user_agent}, language={self.profile.language}>")


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



	def check_in(self, tz: int = None) -> DynamicObject:
		return self.req.request("POST", f"/x{self.comId}/s/check-in", { "timezone": tz if tz else timezone()})


	def get_invite_codes(self, status: str = "normal", start: int = 0, size: int = 25):
		return self.req.request("GET", f"/g/s-x{self.comId}/community/invitation?status={status}&start={start}&size={size}")["communityInvitationList"]

	def generate_invite_code(self, duration: int = 0, force: bool = True):

		data = {
			"duration": duration,
			"force": force
		}
		return self.req.request("POST", f"/g/s-x{self.comId}/community/invitation", data)["communityInvitation"]

	def delete_invite_code(self, inviteId: str):
		return self.req.request("DELETE", f"/g/s-x{self.comId}/community/invitation/{inviteId}")

	def post_blog(self, title: str, content: str, imageList: list = None, captionList: list = None, categoriesList: list = None, backgroundColor: str = None, fansOnly: bool = False, extensions: dict = None):
		
		mediaList = []

		if captionList is not None:
			for image, caption in zip(imageList, captionList):
				mediaList.append([100, self.req.upload_media(image).mediaValue, caption])
		else:
			if imageList is not None:
				for image in imageList:
					mediaList.append([100, self.req.upload_media(image).mediaValue, None])
		
		data = {
			"address": None,
			"content": content,
			"title": title,
			"mediaList": mediaList,
			"extensions": extensions,
			"latitude": 0,
			"longitude": 0,
			"eventSource": "GlobalComposeMenu",
		}

		if fansOnly:
			data["extensions"] = {"fansOnly": fansOnly}
		if backgroundColor:
			data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if categoriesList:
			data["taggedBlogCategoryIdList"] = categoriesList
		return self.req.request("POST", f"/x{self.comId}/s/blog", data)


	def post_wiki(self, title: str, content: str, icon: str = None, imageList: list = None, keywords: str = None, backgroundColor: str = None, props: list = None, backgroundMediaList: list = None):

		data = {
			"label": title,
			"content": content,
			"mediaList": imageList if imageList else [],
			"eventSource": "GlobalComposeMenu",
			"extensions": {},
		}
		if icon:
			data["icon"] = icon
		if keywords:
			data["keywords"] = keywords
		if props:
			data["extensions"].update({"props": props})
		if backgroundMediaList:
			data["extensions"].update({"style": {"backgroundMediaList": backgroundMediaList}})
		if backgroundColor:
			data["extensions"].update({"style": {"backgroundColor": backgroundColor}})

		return self.req.request("POST", f"/x{self.comId}/s/item", data)


	def edit_blog(self, blogId: str, title: str = None, content: str = None, imageList: list = None, categoriesList: list = None, backgroundColor: str = None, fansOnly: bool = False):
		mediaList = []

		for image in imageList:
			mediaList.append([100, self.req.upload_media(image).mediaValue, None])

		data = {
			"address": None,
			"mediaList": mediaList,
			"latitude": 0,
			"longitude": 0,
			"eventSource": "PostDetailView",
		}

		if title: data["title"] = title
		if content: data["content"] = content
		if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
		if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if categoriesList: data["taggedBlogCategoryIdList"] = categoriesList
		return self.req.request("POST", f"/x{self.comId}/s/blog/{blogId}", data)

	def delete_blog(self, blogId: str):
		return self.req.request("DELETE", f"/x{self.comId}/s/blog/{blogId}")

	def delete_wiki(self, wikiId: str):
		return self.req.request("DELETE", f"/x{self.comId}/s/item/{wikiId}") 

	def repost_blog(self, content: str = None, blogId: str = None, wikiId: str = None):
		if blogId is None and wikiId is None: raise SpecifyType

		data = {
			"content": content,
			"refObjectId": blogId if blogId else wikiId,
			"refObjectType": 1 if blogId else 2,
			"type": 2,
		}

		return self.req.request("POST", f"/x{self.comId}/s/blog", data)

	def repair_check_in(self, repair_method: str = RepairMethod.Coins):
		if repair_method not in RepairMethod.all: raise WrongType
		data = {
			"repairMethod": repair_method
		}

		return self.req.request("POST", f"/x{self.comId}/s/check-in/repair", data)


	def check_in(self, tz: int = None) -> DynamicObject:
		return self.req.request("POST", f"/x{self.comId}/s/check-in", { "timezone": tz if tz else timezone()})


	def lottery(self, tz: int = None):
		return self.req.request("POST", f"/x{self.comId}/s/check-in/lottery", { "timezone": tz if tz else timezone()})["lotteryLog"]

	def edit_profile(self, nickname: str = None, content: str = None, icon: BinaryIO = None, chatRequestPrivilege: str = None, imageList: list = None, captionList: list = None, backgroundImage: str = None, backgroundColor: str = None, titles: list = None, colors: list = None, defaultBubbleId: str = None):
		mediaList = []
		data = {}
		if captionList is not None:
			for image, caption in zip(imageList, captionList):
				mediaList.append([100, self.req.upload_media(image).mediaValue, caption])
		else:
			if imageList is not None:
				for image in imageList:
					mediaList.append([100, self.req.upload_media(image).mediaValue, None])

		if imageList is not None or captionList is not None:data["mediaList"] = mediaList
		if nickname:data["nickname"] = nickname
		if icon:data["icon"] = self.req.upload_media(icon).mediaValue
		if content:data["content"] = content
		if chatRequestPrivilege:data["extensions"] = {"privilegeOfChatInviteRequest": chatRequestPrivilege}
		if backgroundImage:
			data["extensions"] = {"style": {
				"backgroundMediaList": [[100, backgroundImage, None, None, None]]
				}}
		if backgroundColor:data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if defaultBubbleId:data["extensions"] = {"defaultBubbleId": defaultBubbleId}
		if titles or colors:
			tlt = []
			for titles, colors in zip(titles, colors):
				tlt.append({"title": titles, "color": colors})
			data["extensions"] = {"customTitles": tlt}

		return self.req.request("POST",  f"/x{self.comId}/s/user-profile/{self.userId}", data)

	def vote_poll(self, blogId: str, optionId: str):
		data = {
			"value": 1,
			"eventSource": "PostDetailView"
		}
		return self.req.request("POST",  f"x{self.comId}/s/blog/{blogId}/poll/option/{optionId}/vote", data)


	def comment(self, message: str, userId: str = None, blogId: str = None, wikiId: str = None, replyTo: str = None, isGuest: bool = False):

		data = {
			"content": message,
			"stickerId": None,
			"type": 0
		}
		if replyTo: data["respondTo"] = replyTo
		if isGuest: comType = "g-comment"
		else: comType = "comment"

		if userId:
			data["eventSource"] = "UserProfileView"
			url = f"/x{self.comId}/s/user-profile/{userId}/{comType}"
		elif blogId:
			data["eventSource"] = "PostDetailView"
			url = f"/x{self.comId}/s/blog/{blogId}/{comType}"
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/x{self.comId}/s/item/{wikiId}/{comType}"
		else: raise SpecifyType

		return self.req.request("POST",  url, data)
						  
	def delete_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):

		if userId:url = f"/x{self.comId}/s/user-profile/{userId}/comment/{commentId}"
		elif blogId:url = f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}"
		elif wikiId:url = f"/x{self.comId}/s/item/{wikiId}/comment/{commentId}"
		else:raise SpecifyType

		return self.req.request("DELETE",  url)

	def like_blog(self, blogId: Union[str, list] = None, wikiId: str = None):

		data = {"value": 4}
		if blogId:
			if isinstance(blogId, str):
				data["eventSource"] = "UserProfileView"
				url = f"/x{self.comId}/s/blog/{blogId}/vote?cv=1.2"
			elif isinstance(blogId, list):
				data["targetIdList"] = blogId
				url = f"/x{self.comId}/s/feed/vote"
			else: raise WrongType(f"blogId: {type(blogId)}")

		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/x{self. comId}/s/item/{wikiId}/vote?cv=1.2"

		else: raise SpecifyType

		return self.req.request("POST",  url, data)

	def unlike_blog(self, blogId: str = None, wikiId: str = None):
		if blogId: url = f"/x{self.comId}/s/blog/{blogId}/vote?eventSource=UserProfileView"
		elif wikiId: url = f"/x{self.comId}/s/item/{wikiId}/vote?eventSource=PostDetailView"
		else: raise SpecifyType

		return self.req.request("DELETE",  url)

	def like_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
		data = {"value": 1}

		if userId:
			data["eventSource"] = "UserProfileView"
			url = f"/x{self.comId}/s/user-profile/{userId}/comment/{commentId}/vote?cv=1.2&value=1"
		elif blogId:
			data["eventSource"] = "PostDetailView"
			url = f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1"
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/x{self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?cv=1.2&value=1"
		else:raise SpecifyType

		return self.req.request("POST",  url, data)

	def unlike_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
		if userId:url = f"/x{self.comId}/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView"
		elif blogId:url = f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		elif wikiId:url = f"/x{self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		else:raise SpecifyType

		return self.req.request("DELETE",  url)

	def upvote_comment(self, blogId: str, commentId: str):
		data = {
			"value": 1,
			"eventSource": "PostDetailView"
		}

		return self.req.request("POST",  f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1", data)

	def downvote_comment(self, blogId: str, commentId: str):
		data = {
			"value": -1,
			"eventSource": "PostDetailView"
		}

		return self.req.request("POST",  f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1", data)

	def unvote_comment(self, blogId: str, commentId: str):
		return self.req.request("DELETE",  f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?eventSource=PostDetailView")

	def reply_wall(self, userId: str, commentId: str, message: str):
		data = {
			"content": message,
			"stackedId": None,
			"respondTo": commentId,
			"type": 0,
			"eventSource": "UserProfileView"
		}

		return self.req.request("POST",  f"/x{self.comId}/s/user-profile/{userId}/comment", data)

	def send_active_obj(self, startTime: int = None, endTime: int = None, tz: int = None, timers: list = None):
		data = {
			"userActiveTimeChunkList": [{
				"start": startTime,
				"end": endTime
			}],
			"optInAdsFlags": 2147483647,
			"timezone": tz if tz else timezone()
		}
		if timers: data["userActiveTimeChunkList"] = timers

		return self.req.request("POST",  f"/x{self.comId}/s/community/stats/user-active-time", data)

	def activity_status(self, status: bool):
		data = {
			"onlineStatus": "on" if status is True else "off",
			"duration": 86400
		}

		return self.req.request("POST",  f"/x{self.comId}/s/user-profile/{self.profile.userId}/online-status", data)

	def check_notifications(self):
		return self.req.request("POST",  f"/x{self.comId}/s/notification/checked")

	def delete_notification(self, notificationId: str):
		return self.req.request("DELETE",  f"/x{self.comId}/s/notification/{notificationId}")

	def clear_notifications(self):
		return self.req.request("DELETE",  f"/x{self.comId}/s/notification")
	
	def start_chat(self, userId: Union[str, list, tuple], message: str, title: str = None, content: str = None, isGlobal: bool = False, publishToGlobal: bool = False):
		if isinstance(userId, str): userIds = [userId]
		elif isinstance(userId, list): userIds = userId
		elif isinstance(userId, tuple): userIds = userId
		else: raise WrongType(f"userId: {type(userId)}")

		data = {
			"title": title,
			"inviteeUids": userIds,
			"initialMessageContent": message,
			"content": content
		}

		if isGlobal is True:
			data["type"] = 2
			data["timestamp"] = "GlobalComposeMenu"
		else:data["type"] = 0
		if publishToGlobal is True:data["publishToGlobal"] = 1
		else:data["publishToGlobal"] = 0

		return self.req.request("POST",  f"/x{self.comId}/s/chat/thread", data)["thread"]

	def invite_to_chat(self, userId: Union[str, list, tuple], chatId: str):
		if isinstance(userId, str): userIds = [userId]
		elif isinstance(userId, list): userIds = userId
		elif isinstance(userId, tuple): userIds = userId
		else: raise WrongType(f"userId: {type(userId)}")
		data = { "uids": userIds }

		return self.req.request("POST",  f"/x{self.comId}/s/chat/thread/{chatId}/member/invite", data)

	def add_to_favorites(self, userId: str):
		return self.req.request("POST",  f"/x{self.comId}/s/user-group/quick-access/{userId}")
	
	def send_coins(self, coins: int, blogId: str = None, chatId: str = None, objectId: str = None, transactionId: str = None):
		data = {
			"coins": coins,
			"tippingContext": {"transactionId": transactionId if transactionId else uuid4()}
		}

		if blogId is not None: url = f"/x{self.comId}/s/blog/{blogId}/tipping"
		elif chatId is not None: url = f"/x{self.comId}/s/chat/thread/{chatId}/tipping"
		elif objectId is not None:
			data["objectId"] = objectId
			data["objectType"] = 2
			url = f"/x{self.comId}/s/tipping"
		else: raise SpecifyType

		return self.req.request("POST", url, data)

	def thank_tip(self, chatId: str, userId: str):
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users/{userId}/thank")

	def follow(self, userId: Union[str, list]):
		
		if isinstance(userId, str):
			return self.req.request("POST", f"/x{self.comId}/s/user-profile/{userId}/member")
		elif isinstance(userId, list):
			data = { "targetUidList": userId }
			return self.req.request("POST", f"/x{self.comId}/s/user-profile/{self.userId}/joined", data)
		else: raise WrongType(f"userId: {type(userId)}")

	def unfollow(self, userId: str):
		return self.req.request("DELETE", f"/x{self.comId}/s/user-profile/{self.userId}/joined/{userId}")

	def block(self, userId: str):
		return self.req.request("POST",  f"/x{self.comId}/s/block/{userId}")

	def unblock(self, userId: str):
		return self.req.request("DELETE",  f"/x{self.comId}/s/block/{userId}")

	def flag(self, reason: str, flagType: int, userId: str = None, blogId: str = None, wikiId: str = None, asGuest: bool = False):

		data = {
			"flagType": flagType,
			"message": reason
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
		else: raise SpecifyType

		return self.req.request("POST",  f"/x{self.comId}/s/{'g-flag' if asGuest else 'flag'}", data)

	def send_message(self, chatId: str, message: str = None, messageType: int = MessageTypes.Text, file: BinaryIO = None, replyTo: str = None, mentionUserIds: list = None, stickerId: str = None, embedId: str = None, embedType: int = None, embedLink: str = None, embedTitle: str = None, embedContent: str = None, embedImage: BinaryIO = None):
		data = {
			"type": messageType,
			"content": message
		}
		if	any(obj is None for obj in [embedId, embedType, embedLink, embedTitle, embedContent, embedImage]):
			attachedObject = {}
			if embedId:attachedObject["objectId"] = embedId
			if embedType:attachedObject["objectType"] = embedType
			if embedLink:attachedObject["link"] = embedLink
			if embedTitle:attachedObject["title"] = embedTitle
			if embedContent:attachedObject["content"] = embedContent
			if embedImage:attachedObject["mediaList"] = [[100, self.req.upload_media(embedImage).mediaValue, None]]
			data["attachedObject"] = attachedObject
		if mentionUserIds:
			mentions = [{"uid": mention_uid} for mention_uid in mentionUserIds]
			data["extensions"] = {"mentionedArray": mentions}
		if replyTo: data["replyMessageId"] = replyTo
		if stickerId:
			data["content"] = None
			data["stickerId"] = stickerId
			data["type"] = MessageTypes.Sticker
		if file:
			data["content"] = None
			fileType = guess_type(file.name)[0]
			if fileType == UploadType.audio:
				data["type"] =  MessageTypes.Voice
				data["mediaType"] = 110
				data["mediaUploadValue"] = b64encode(file.read()).decode()
			else:
				url = self.req.upload_media(file).mediaValue
				data["mediaValue"] = url
		return self.req.request("POST",  f"/x{self.comId}/s/chat/thread/{chatId}/message", data)

	def send_full_embed(self, link: str, image: BinaryIO, message: str, chatId: str):
		url = self.req.upload_media(image).mediaValue
		data = {
			"type": MessageTypes.Text,
			"content": message,
			"extensions": {
				"linkSnippetList": [{
					"link": link,
					"mediaValue": url
				}]
			},
			"attachedObject": None
		}

		return self.req.request("POST",  f"/x{self.comId}/s/chat/thread/{chatId}/message", data)

	def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str = None):

		if asStaff:
			data = {
				"adminOpName": 102,
			}
			if reason:data["adminOpNote"] = {"content": reason}
			return self.req.request("POST",  f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}/admin", data)
		return self.req.request("DELETE",  f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}")

	def mark_as_read(self, chatId: str, messageId: str):
		data = {"messageId": messageId}
		return self.req.request("POST",  f"/x{self.comId}/s/chat/thread/{chatId}/mark-as-read", data)

	def edit_chat(self, chatId: str, title: str = None, icon: str = None, content: str = None, announcement: str = None, keywords: list = None, pinAnnouncement: bool = None, publishToGlobal: bool = None, fansOnly: bool = None):
		data = {}
		
		if title: data["title"] = title
		if content: data["content"] = content
		if icon: data["icon"] = icon
		if keywords: data["keywords"] = keywords
		if announcement: data["extensions"] = {"announcement": announcement}
		if pinAnnouncement: data["extensions"] = {"pinAnnouncement": pinAnnouncement}
		if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
		if publishToGlobal is not None: data["publishToGlobal"] = 0 if publishToGlobal else 1

		return self.req.request("POST",  f"/x{self.comId}/s/chat/thread/{chatId}", data)

	def do_not_disturb(self, chatId: str, doNotDisturb: bool = True) -> DynamicObject:
		data = {
			"alertOption": 2 if doNotDisturb else 1,
		}
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.userId}/alert", data)

	def pin_chat(self, chatId: str, pin: bool = True) -> DynamicObject:
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}{'pin' if pin else 'unpin'}", {})


	def set_chat_background(self, chatId: str, backgroundImage: BinaryIO) -> DynamicObject:
		data = {
			"media": [100, self.req.upload_media(backgroundImage).mediaValue, None]
		}
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.userId}/background", data)
	
	def add_co_hosts(self, chatId: str, coHosts: list) -> DynamicObject:
		data = {
			"uidList": coHosts
		}
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/co-host", data)


	def delete_co_host(self, chatId: str, userId: str) -> DynamicObject:
		return self.req.request("DELETE", f"/x{self.comId}/chat/thread/{chatId}/co-host/{userId}")


	def chat_view_only(self, chatId: str, viewOnly: bool = False) -> DynamicObject:
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/view-only/{'enable' if viewOnly else 'disable'}")
	
	def member_can_invite_to_chat(self, chatId: str, canInvite: bool = True) -> DynamicObject:
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/members-can-invite/{'enable' if canInvite else 'disable'}")

	def member_can_chat_tip(self, chatId: str, canTip: bool = True) -> DynamicObject:
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/tipping-perm-status/{'enable' if canTip else 'disable'}")

	def transfer_host(self, chatId: str, userIds: list):
		data = { "uidList": userIds }
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer", data)

	def accept_host(self, chatId: str, requestId: str):
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept")

	def kick(self, userId: str, chatId: str, allowRejoin: bool = True):
		return self.req.request("DELETE", f"/x{self.comId}/s/chat/thread/{chatId}/member/{userId}?allowRejoin={int(allowRejoin)}")

	def join_chat(self, chatId: str):
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.userId}")

	def leave_chat(self, chatId: str):
		return self.req.request("DELETE", f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.userId}")

	def delete_chat(self, chatId: str):
		return self.req.request("DELETE", f"/x{self.comId}/s/chat/thread/{chatId}")

	def subscribe_influencer(self, userId: str, autoRenew: str = False, transactionId: str = None):
		data = {
			"paymentContext": {
				"transactionId": transactionId if transactionId else str(uuid4()),
				"isAutoRenew": autoRenew
			}
		}
		return self.req.request("POST", f"/x{self.comId}/s/influencer/{userId}/subscribe", data)

	def promotion(self, noticeId: str, type: str = "accept"):
		return self.req.request("POST", f"/x{self.comId}/s/notice/{noticeId}/{type}")

	def play_quiz_raw(self, quizId: str, quizAnswerList: list, quizMode: int = 0):
		data = {
			"mode": quizMode,
			"quizAnswerList": quizAnswerList
		}

		return self.req.request("POST", f"/x{self.comId}/s/blog/{quizId}/quiz/result", data)

	def play_quiz(self, quizId: str, questionIdsList: list, answerIdsList: list, quizMode: int = 0):
		data = {
			"mode": quizMode,
			"quizAnswerList": list()
		}
		for question, answer in zip(questionIdsList, answerIdsList):
			data["quizAnswerList"].append({
				"optIdList": [answer],
				"quizQuestionId": question,
				"timeSpent": 0.0
			})
		
		return self.req.request("POST", f"/x{self.comId}/s/blog/{quizId}/quiz/result", data)

	def vc_permission(self, chatId: str, permission: int = VoiceChatJoinPermissions.Open):
		data = { "vvChatJoinType": permission }
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/vvchat-permission", data)

	def get_vc_reputation_info(self, chatId: str):
		return self.req.request("GET", f"/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation")

	def claim_vc_reputation(self, chatId: str):
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation")

	def get_all_users(self, type: str = UsersTypes.Recent, start: int = 0, size: int = 25):
		if type not in UsersTypes.all:raise WrongType(f"type: {type} not in {UsersTypes.all}")
		return self.req.request("GET", f"/x{self.comId}/s/user-profile?type={type}&start={start}&size={size}")

	def get_online_users(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/live-layer?topic=ndtopic:x{self.comId}:online-members&start={start}&size={size}")

	def get_online_favorite_users(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/user-group/quick-access?type=online&start={start}&size={size}")

	def get_user_info(self, userId: str):
		return self.req.request("GET", f"/x{self.comId}/s/user-profile/{userId}")["userProfile"]

	def get_user_following(self, userId: str, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/user-profile/{userId}/joined?start={start}&size={size}")["userProfileList"]

	def get_user_followers(self, userId: str, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/user-profile/{userId}/member?start={start}&size={size}")["userProfileList"]

	def get_user_checkins(self, userId: str):
		return self.req.request("GET", f"/x{self.comId}/s/check-in/stats/{userId}?timezone={timezone()}")

	def get_user_blogs(self, userId: str, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/blog?type=user&q={userId}&start={start}&size={size}")["blogList"]

	def get_user_wikis(self, userId: str, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/item?type=user-all&start={start}&size={size}&cv=1.2&uid={userId}")["itemList"]

	def get_user_achievements(self, userId: str):
		return self.req.request("GET", f"/x{self.comId}/s/user-profile/{userId}/achievements")["achievements"]

	def get_influencer_fans(self, userId: str, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/influencer/{userId}/fans?start={start}&size={size}")

	def get_blocked_users(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/block?start={start}&size={size}")["userProfileList"]

	def get_blocker_users(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/block?start={start}&size={size}")["blockerUidList"]

	def search_users(self, nickname: str, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/user-profile?type=name&q={nickname}&start={start}&size={size}")["userProfileList"]

	def get_saved_blogs(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/bookmark?start={start}&size={size}")["bookmarkList"]

	def get_leaderboard_info(self, type: str = LeaderboardTypes.Day, start: int = 0, size: int = 25):
		if type not in LeaderboardTypes.all:raise WrongType(f"LeaderboardTypes.all: {type} not in {LeaderboardTypes.all}")
		url = f"/g/s-x{self.comId}/community/leaderboard?rankingType={type}&start={start}"
		if type != 4:url += f"&size={size}"

		return self.req.request("GET", url)["userProfileList"]


	def get_wiki_info(self, wikiId: str):
		return self.req.request("GET", f"/x{self.comId}/s/item/{wikiId}")

	def get_recent_wiki_items(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/item?type=catalog-all&start={start}&size={size}")["itemList"]

	def get_wiki_categories(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/item-category?start={start}&size={size}")["itemCategoryList"]

	def get_wiki_category(self, categoryId: str, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/item-category/{categoryId}?pagingType=t&start={start}&size={size}")

	def get_tipped_users(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, chatId: str = None, start: int = 0, size: int = 25):
		object_types = {
			'blogId': {'id': blogId or quizId, 'url': f"/x{self.comId}/s/blog/{blogId or quizId}/tipping/tipped-users-summary"},
			'wikiId': {'id': wikiId, 'url': f"/x{self.comId}/s/item/{wikiId}/tipping/tipped-users-summary"},
			'chatId': {'id': chatId, 'url': f"/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users-summary"},
			'fileId': {'id': fileId, 'url': f"/x{self.comId}/s/shared-folder/files/{fileId}/tipping/tipped-users-summary"}
		}
		for key, value in object_types.items():
			if value['id']:return self.req.request("GET", f"{value['url']}?start={start}&size={size}")
		else:raise SpecifyType


	def get_chat_threads(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/chat/thread?type=joined-me&start={start}&size={size}")["threadList"]

	def get_public_chat_threads(self, type: str = "recommended", start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/chat/thread?type=public-all&filterType={type}&start={start}&size={size}")["threadList"]

	def get_chat_thread(self, chatId: str):
		return self.req.request("GET", f"/x{self.comId}/s/chat/thread/{chatId}")["thread"]

	def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str = None):
		return self.req.request("GET", f"/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}{f'&pageToken={pageToken}' if pageToken else  ''}")

	def get_message_info(self, chatId: str, messageId: str):
		return self.req.request("GET", f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}")["message"]

	def get_blog_info(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None):
		if blogId or quizId:
			return self.req.request("GET", f"/x{self.comId}/s/blog/{blogId or quizId}")
		elif wikiId:
			return self.req.request("GET", f"/x{self.comId}/s/item/{wikiId}")
		elif fileId:
			return self.req.request("GET", f"/x{self.comId}/s/shared-folder/files/{fileId}")["file"]
		raise SpecifyType

	def get_blog_comments(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, sorting: str = Sorting.Newest, start: int = 0, size: int = 25):
		if sorting not in Sorting.all:raise ValueError(f"Sorting.all: {sorting} not in {Sorting.all}")
		object_types = {
			'blogId': {'id': blogId or quizId, 'url': f"/x{self.comId}/s/blog/{blogId or quizId}/comment"},
			'wikiId': {'id': wikiId, 'url': f"/x{self.comId}/s/item/{wikiId}/comment"},
			'fileId': {'id': fileId, 'url': f"/x{self.comId}/s/shared-folder/files/{fileId}/comment"}
		}

		for key, value in object_types.items():
			if value['id']:
				return self.req.request("GET", f"{value['url']}?sort={sorting}&start={start}&size={size}")["commentList"]
		else:
			raise SpecifyType


	def get_blog_categories(self, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/blog-category?size={size}")["blogCategoryList"]

	def get_blogs_by_category(self, categoryId: str,start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/blog-category/{categoryId}/blog-list?start={start}&size={size}")["blogList"]

	def get_quiz_rankings(self, quizId: str, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/blog/{quizId}/quiz/result?start={start}&size={size}")

	def get_wall_comments(self, userId: str, sorting: str = Sorting.Newest, start: int = 0, size: int = 25):
		if sorting not in Sorting.all:raise ValueError(f"Sorting.all: {sorting} not in {Sorting.all}")
		return self.req.request("GET", f"/x{self.comId}/s/user-profile/{userId}/comment?sort={sorting}&start={start}&size={size}")["commentList"]

	def get_recent_blogs(self, pageToken: str = None, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/feed/blog-all?pagingType=t&start={start}&size={size}{f'&pageToken={pageToken}' if pageToken else  ''}")

	def get_chat_users(self, chatId: str, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/chat/thread/{chatId}/member?type=default&cv=1.2&start={start}&size={size}")["memberList"]

	def get_notifications(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/notification?pagingType=t&start={start}&size={size}")["notificationList"]

	def get_notices(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/notice?type=usersV2&status=1&start={start}&size={size}")["noticeList"]

	def get_sticker_pack_info(self, sticker_pack_id: str):
		return self.req.request("GET", f"/x{self.comId}/s/sticker-collection/{sticker_pack_id}?includeStickers=true")["stickerCollection"]

	def get_my_sticker_packs(self):
		return self.req.request("GET", f"/x{self.comId}/s/sticker-collection?includeStickers=false&type=my-active-collection")["stickerCollection"]

	def get_store_chat_bubbles(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/store/items?sectionGroupId=chat-bubble&start={start}&size={size}")
	
	def get_store_stickers(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/store/items?sectionGroupId=sticker&start={start}&size={size}")

	def get_community_stickers(self):
		return self.req.request("GET", f"/x{self.comId}/s/sticker-collection?type=community-shared")

	def get_sticker_collection(self, collectionId: str):
		return self.req.request("GET", f"/x{self.comId}/s/sticker-collection/{collectionId}?includeStickers=true")["stickerCollection"]

	def get_shared_folder_info(self):
		return self.req.request("GET", f"/x{self.comId}/s/shared-folder/stats")["stats"]

	def get_shared_folder_files(self, type: str = "latest", start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/shared-folder/files?type={type}&start={start}&size={size}")["fileList"]

	#
	# MODERATION MENU
	#

	def moderation_history(self, userId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, size: int = 25):
		object_types = {
			'userId': {'id': userId, 'type': 0},
			'blogId': {'id': blogId, 'type': 1},
			'wikiId': {'id': wikiId, 'type': 2},
			'quizId': {'id': quizId, 'type': 1},
			'fileId': {'id': fileId, 'type': 109}
		}

		for key, value in object_types.items():
			if value['id']:
				url = f"/x{self.comId}/s/admin/operation?objectId={value['id']}&objectType={value['type']}&pagingType=t&size={size}"
				break
		else:
			url = f"/x{self.comId}/s/admin/operation?pagingType=t&size={size}"
		return self.req.request("GET", url)["adminLogList"]

	def feature(self, time: int, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None):
		if chatId:
			if time == 1: time = 3600
			if time == 1: time = 7200
			if time == 1: time = 10800

		else:
			if time == 1: time = 86400
			elif time == 2: time = 172800
			elif time == 3: time = 259200
			else: raise WrongType(time)

		data = {
			"adminOpName": 114,
			"adminOpValue": {
				"featuredDuration": time
			}
		}

		if userId:
			data["adminOpValue"] = {"featuredType": 4}
			url = f"/x{self.comId}/s/user-profile/{userId}/admin"
		elif blogId:
			data["adminOpValue"] = {"featuredType": 1}
			url = f"/x{self.comId}/s/blog/{blogId}/admin"
		elif wikiId:
			data["adminOpValue"] = {"featuredType": 1}
			url = f"/x{self.comId}/s/item/{wikiId}/admin"
		elif chatId:
			data["adminOpValue"] = {"featuredType": 5}
			url = f"/x{self.comId}/s/chat/thread/{chatId}/admin"
		else: raise SpecifyType

		return self.req.request("POST", url, data)

	def unfeature(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None):
		data = {
			"adminOpName": 114,
			"adminOpValue": {"featuredType": 0}
		}

		if userId:
			url = f"/x{self.comId}/s/user-profile/{userId}/admin"
		elif blogId:
			url = f"/x{self.comId}/s/blog/{blogId}/admin"
		elif wikiId:
			url = f"/x{self.comId}/s/item/{wikiId}/admin"
		elif chatId:
			url = f"/x{self.comId}/s/chat/thread/{chatId}/admin"
		else: raise SpecifyType

		return self.req.request("POST", url, data)

	def hide(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, reason: str = None):
		data = {
			"adminOpNote": {
				"content": reason
			}
		}

		if userId:
			data["adminOpName"] = 18
			url = f"/x{self.comId}/s/user-profile/{userId}/admin"
		elif blogId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 9
			url = f"/x{self.comId}/s/blog/{blogId}/admin"
		elif quizId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 9
			url = f"/x{self.comId}/s/blog/{quizId}/admin"
		elif wikiId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 9
			url = f"/x{self.comId}/s/item/{wikiId}/admin"
		elif chatId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 9
			url = f"/x{self.comId}/s/chat/thread/{chatId}/admin"
		elif fileId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 9
			url = f"/x{self.comId}/s/shared-folder/files/{fileId}/admin"
		else: raise SpecifyType

		return self.req.request("POST", url, data)

	def unhide(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, reason: str = None):
		data = {
			"adminOpNote": {
				"content": reason
			}
		}

		if userId:
			data["adminOpName"] = 19
			url = f"/x{self.comId}/s/user-profile/{userId}/admin"
		elif blogId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 0
			url = f"/x{self.comId}/s/blog/{blogId}/admin"
		elif quizId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 0
			url = f"/x{self.comId}/s/blog/{quizId}/admin"
		elif wikiId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 0
			url = f"/x{self.comId}/s/item/{wikiId}/admin"
		elif chatId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 0
			url = f"/x{self.comId}/s/chat/thread/{chatId}/admin"
		elif fileId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 0
			url = f"/x{self.comId}/s/shared-folder/files/{fileId}/admin"
		else: raise SpecifyType

		return self.req.request("POST", url, data)

	def edit_titles(self, userId: str, titles: list):

		data = {
			"adminOpName": 207,
			"adminOpValue": {
				"titles": titles
			}
		}

		return self.req.request("POST", f"/x{self.comId}/s/user-profile/{userId}/admin", data)

	
	def warn(self, userId: str, reason: str = None):
		data = {
			"uid": userId,
			"title": "Custom",
			"content": reason,
			"attachedObject": {
				"objectId": userId,
				"objectType": 0
			},
			"penaltyType": 0,
			"adminOpNote": {},
			"noticeType": 7
		}

		return self.req.request("POST", f"/x{self.comId}/s/notice", data)

	
	def strike(self, userId: str, time: int, title: str = None, reason: str = None):
		if time == 1:
			time = 86400
		elif time == 2:
			time = 10800
		elif time == 3:
			time = 21600
		elif time == 4:
			time = 43200
		elif time == 5:
			time = 86400
		else:
			raise WrongType(time)

		data = {
			"uid": userId,
			"title": title,
			"content": reason,
			"attachedObject": {
				"objectId": userId,
				"objectType": 0
			},
			"penaltyType": 1,
			"penaltyValue": time,
			"adminOpNote": {},
			"noticeType": 4
		}
		return self.req.request("POST", f"/x{self.comId}/s/notice", data)

	def ban(self, userId: str, reason: str, banType: int = None):
		data = {
			"reasonType": banType,
			"note": {
				"content": reason
			}
		}
		return self.req.request("POST", f"/x{self.comId}/s/user-profile/{userId}/ban", data)

	def unban(self, userId: str, reason: str):
		data = {
			"note": {
				"content": reason
			}
		}

		return self.req.request("POST", f"/x{self.comId}/s/user-profile/{userId}/unban", data)

	def reorder_featured_users(self, userIds: list):
		data = { "uidList": userIds }
		return self.req.request("POST", f"/x{self.comId}/s/user-profile/featured/reorder", data)

	def get_hidden_blogs(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/feed/blog-disabled?start={start}&size={size}")["blogList"]
	

	def get_featured_users(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/user-profile?type=featured&start={start}&size={size}")

	def review_quiz_questions(self, quizId: str):
		return self.req.request("GET", f"/x{self.comId}/s/blog/{quizId}?action=review")["blog"]["quizQuestionList"]

	def get_recent_quiz(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/blog?type=quizzes-recent&start={start}&size={size}")["blogList"]

	def get_trending_quiz(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/feed/quiz-trending?start={start}&size={size}")["blogList"]

	def get_best_quiz(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/feed/quiz-best-quizzes?start={start}&size={size}")["blogList"]


	def purchase(self, objectId: str, objectType: int, aminoPlus: bool = True, autoRenew: bool = False):
		data = {
			"objectId": objectId,
			"objectType": objectType,
			"v": 1,
			"paymentContext": {
				'discountStatus': 1 if aminoPlus is True else 0,
				'discountValue': 1,
				'isAutoRenew': autoRenew
			}
		}

		return self.req.request("POST", f"/x{self.comId}/s/store/purchase", data)


	def apply_avatar_frame(self, avatarId: str, applyToAll: bool = True):
		data = {
			"frameId": avatarId,
			"applyToAll": 1 if applyToAll is True else 0,
		}
		return self.req.request("POST", f"/x{self.comId}/s/avatar-frame/apply", data)

	def invite_to_vc(self, chatId: str, userId: str):
		data = { "uid": userId }
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/vvchat-presenter/invite/", data)

	def add_poll_option(self, blogId: str, question: str):
		data = {
			"mediaList": None,
			"title": question,
			"type": 0
		}
		return self.req.request("POST", f"/x{self.comId}/s/blog/{blogId}/poll/option", data)

	def create_wiki_category(self, title: str, parentCategoryId: str, media: list = None):
		data = {
			"icon": None,
			"label": title,
			"mediaList": media,
			"parentCategoryId": parentCategoryId,
		}
		return self.req.request("POST", f"/x{self.comId}/s/item-category", data)
		
	def create_shared_folder(self,title: str):
		data = { "title": title }
		return self.req.request("POST", f"/x{self.comId}/s/shared-folder/folders", data)

	def submit_to_wiki(self, wikiId: str, message: str):
		data = {
			"message": message,
			"itemId": wikiId
		}
		return self.req.request("POST", f"/x{self.comId}/s/knowledge-base-request", data)

	def accept_wiki_request(self, requestId: str, destinationCategoryIdList: list):
		data = {
			"destinationCategoryIdList": destinationCategoryIdList,
			"actionType": "create"
		}

		return self.req.request("POST", f"/x{self.comId}/s/knowledge-base-request/{requestId}/approve", data)

	def reject_wiki_request(self, requestId: str):
		data = {}
		return self.req.request("POST", f"/x{self.comId}/s/knowledge-base-request/{requestId}/reject", data)

	def get_wiki_submissions(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/knowledge-base-request?type=all&start={start}&size={size}")["knowledgeBaseRequestList"]

	def get_live_layer(self):
		return self.req.request("GET", f"/x{self.comId}/s/live-layer/homepage?v=2")["liveLayerList"]

	def apply_bubble(self, bubbleId: str, chatId: str, applyToAll: bool = False):
		data = {
			"applyToAll": 1 if applyToAll is True else 0,
			"bubbleId": bubbleId,
			"threadId": chatId,
		}

		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/apply-bubble", data)
		

	"""
	ACM
	"""

	def create_community(self, name: str, tagline: str, icon: BinaryIO, themeColor: str, joinType: int = 0, primaryLanguage: str = "en"):

		data = {
			"icon": {
				"height": 512.0,
				"imageMatrix": [1.6875, 0.0, 108.0, 0.0, 1.6875, 497.0, 0.0, 0.0, 1.0],
				"path": self.req.upload_media(icon).mediaValue,
				"width": 512.0,
				"x": 0.0,
				"y": 0.0
			},
			"joinType": joinType,
			"name": name,
			"primaryLanguage": primaryLanguage,
			"tagline": tagline,
			"templateId": 9,
			"themeColor": themeColor
		}

		return self.req.request("POST", f"/g/s/community", data)


	def get_community_themepack_info(self):
		return self.req.request("POST", f"/g/s-x{self.comId}/community/info?withTopicList=1&withInfluencerList=1&influencerListOrderStrategy=fansCount")['community']['themePack']

	def upload_themepack(self, file: BinaryIO):
		return self.req.request("POST", f"/x{self.comId}/s/media/upload/target/community-theme-pack", data=file.read())

	def delete_community(self, email: str, password: str, verificationCode: str):
		data = {
			"secret": f"0 {password}",
			"validationContext": {
				"data": {
					"code": verificationCode
				},
				"type": 1,
				"identity": email
			},
			"deviceID": self.deviceId
		}
		return self.req.request("POST", f"/g/s-x{self.comId}/community/delete-request", data)

	def my_managed_communities(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/g/s/community/managed?start={start}&size={size}")["communityList"]

	def get_categories(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/blog-category?start={start}&size={size}")

	def change_sidepanel_color(self, color: str):
		data = {
			"path": "appearance.leftSidePanel.style.iconColor",
			"value": color
		}
		return self.req.request("POST", f"/x{self.comId}/s/community/configuration", data)

	def promote(self, userId: str, rank: str):
		if rank not in AdministratorsRank.all:raise SpecifyType(f"[AdministratorsRank.all] -> Available ranks: {AdministratorsRank.all}")
		rank = rank.lower().replace("agent", "transfer-agent")
		return self.req.request("POST", f"/x{self.comId}/s/user-profile/{userId}/{rank}")

	def get_join_requests(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/community/membership-request?status=pending&start={start}&size={size}")
	
	def accept_join_request(self, userId: str):
		data = {}
		return self.req.request("POST", f"/x{self.comId}/s/community/membership-request/{userId}/accept", data)
	
	def reject_join_request(self, userId: str):
		data = {}
		return self.req.request("POST", f"/x{self.comId}/s/community/membership-request/{userId}/reject", data)

	def get_community_stats(self):
		return self.req.request("GET", f"/x{self.comId}/s/community/stats")["communityStats"]

	def get_community_moderation_stats(self, type: str, start: int = 0, size: int = 25):
		if type.lower() not in ("leader", "curator"):raise WrongType(f"{type} not in ('leader', 'curator')")
		return self.req.request("GET", f"/x{self.comId}/s/community/stats/moderation?type={type.lower()}&start={start}&size={size}")["userProfileList"]

	def change_welcome_message(self, message: str, isEnabled: bool = True):

		data = {
			"path": "general.welcomeMessage",
			"value": {
				"enabled": isEnabled,
				"text": message
			}
		}
		return self.req.request("POST", f"/x{self.comId}/s/community/configuration", data)

	def change_community_invite_permission(self, onlyAdmins: bool = True) -> int:
		data = {
			"path": "general.invitePermission",
			"value": 2 if onlyAdmins is True else 1,
			"action": "set"
		}
		return self.req.request("POST", f"/x{self.comId}/s/community/configuration", data)


	def change_community_aminoId(self, aminoId: str):
		data = {
			"endpoint": aminoId,
		}
		return self.req.request("POST", f"/x{self.comId}/s/community/settings", data)

	def change_guidelines(self, message: str):

		data = {"content": message}
		return self.req.request("POST", f"/x{self.comId}/s/community/guideline", data)

	def edit_community(self, name: str = None, description: str = None, aminoId: str = None, primaryLanguage: str = None, themePackUrl: str = None):

		data = {}

		if name is not None:
			data["name"] = name
		if description is not None:
			data["content"] = description
		if aminoId is not None:
			data["endpoint"] = aminoId
		if primaryLanguage is not None:
			data["primaryLanguage"] = primaryLanguage
		if themePackUrl is not None:
			data["themePackUrl"] = themePackUrl
		
		return self.req.request("POST", f"/x{self.comId}/s/community/settings", data)

	def change_module(self, module: str, isEnabled: bool):
		if module not in CommunityModules.all:raise SpecifyType(f"[CommunityModules.all] -> Available community modules: {CommunityModules.all}")
		data = {
			"path": module,
			"value": isEnabled
		}
		return self.req.request("POST", f"/x{self.comId}/s/community/configuration", data)
	
	def add_influencer(self, userId: str, monthlyFee: int):
		data = {
			"monthlyFee": monthlyFee
		}
		return self.req.request("POST", f"/x{self.comId}/s/influencer/{userId}", data)
		

	def remove_influencer(self, userId: str):
		return self.req.request("DELETE", f"/x{self.comId}/s/influencer/{userId}")

	def get_notice_list(self, start: int = 0, size: int = 25):
		return self.req.request("GET", f"/x{self.comId}/s/notice?type=management&status=1&start={start}&size={size}")["noticeList"]

	def delete_pending_role(self, noticeId: str):
		return self.req.request("DELETE", f"/x{self.comId}/s/notice/{noticeId}")