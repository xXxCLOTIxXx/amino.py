from __future__ import annotations

from .objects.auth_data import auth_data
from .helpers.requests_builder import requestsBuilder
from .helpers.generator import timezone, clientrefid
from .helpers.exceptions import SpecifyType, WrongType

from .objects.args import (
	RepairMethod, CommunityModules, UsersTypes,
	AdministratorsRank, VoiceChatJoinPermissions,
	LeaderboardTypes, Sorting, UploadType, MessageTypes,
	PurchaseTypes, PromotionTypes, QuizMode, CommunityJoinTypes,
	Sorting2, FeatureDays, StrikeTime
)

from typing import BinaryIO
from uuid import uuid4
from base64 import b64encode
from mimetypes import guess_type

class CommunityClient:
	"""
		Class for working with amino in community and ACM [https://aminoapps.com/]
		Arguments for the class:
		
		- profile: auth_data
			- account login details (client.profile)
		
		- comId: int
			- ID of the community in which the functions will be performed. can be taken in client functions or at a socket event
			
		- proxies: dict = None
			- dictionary with proxy
			
		- timeout: int | None = None
			- waiting time before request is reset
	"""

	req: requestsBuilder
	comId: str
	
	def __init__(self, profile: auth_data, comId: int, proxies: dict | None = None, timeout: int | None = None):
		self.req = requestsBuilder(proxies=proxies, profile=profile, timeout=timeout)
		self.comId = comId

	def __repr__(self):
		return repr(f"class CommunityClient <sid={self.sid}, userId={self.userId}, comId={self.comId}, deviceId={self.deviceId}, user_agent={self.profile.user_agent}, language={self.profile.language}>")


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



	def check_in(self, tz: int | None = None):
		"""
		Check in community.

		**Parameters**:
		- tz: time zone
			- better dont touch
		"""
		return self.req.request("POST", f"/x{self.comId}/s/check-in", { "timezone": tz if tz else timezone()})


	def get_invite_codes(self, status: str = "normal", start: int = 0, size: int = 25):
		"""
		Get invite codes of community. If you have rights, of course.

		**Parameters**
		- status: str = "normal"
			- ???
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.request("GET", f"/g/s-x{self.comId}/community/invitation?status={status}&start={start}&size={size}")["communityInvitationList"]

	def generate_invite_code(self, duration: int = 0, force: bool = True):
		"""
		Generate invite code for community. If you have rights, of course.

		**Parameters**:
		- duration: int = 0
			- duration of invite code
			- if 0, its will work forever
		- force: bool = True
			- do you want show your force power of siths or no?
		"""
		data = {
			"duration": duration,
			"force": force
		}
		return self.req.request("POST", f"/g/s-x{self.comId}/community/invitation", data)["communityInvitation"]

	def delete_invite_code(self, inviteId: str):
		"""
		Delete invite code from community. If you have rights, of course.

		**Parameters**:
		- inviteId: str
			- its NOT invite code
			- yes, you can get it. using function `get_invite_codes`
		"""
		return self.req.request("DELETE", f"/g/s-x{self.comId}/community/invitation/{inviteId}")


	def get_vip_users(self):
		"""
		Get VIP users of community. VIP is basically fanclubs.
		"""

		return self.req.request("GET", f"/{self.comId}/s/influencer").userProfileList

	def post_blog(self, title: str, content: str, imageList: list | None = None, captionList: list | None = None, categoriesList: list | None = None, backgroundColor: str | None = None, fansOnly: bool = False, extensions: dict | None = None):
		"""
		Posting blog.

		**Parameters**:
		- title: str
		- content: str
		- imageList: list = None
		- captionList: list = None
			- captions for images
		- categoriesList: list = None
		- backgroundColor: str = None
			- should be only hex code, like "#000000"
			- if None, it will be just white
		- fansOnly: bool = False
			- is it for your onlyfans or no?
			- works only if you have fanclub
		- extensions: dict = None
			- maybe your code is tight
		"""
		
		
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


	def post_wiki(self, title: str, content: str, icon: str | None = None, imageList: list | None = None, keywords: str | None = None, backgroundColor: str | None = None, props: list | None = None, backgroundMediaList: list | None = None):
		"""
		Posting wiki.

		**Parameters**:
		- title: str
		- content: str
		- icon: str
		- imageList: list = None
		- keywords: str = None
		- backgroundColor: str = None
			- should be only hex code, like "#000000"
			- if None, it will be just white
		- backgroundMediaList: list
		- props: list
		- fansOnly: bool = False
			- is it for your onlyfans or no?
			- works only if you have fanclub
		"""
		
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


	def edit_blog(self, blogId: str, title: str | None = None, content: str | None = None, imageList: list | None = None, categoriesList: list | None = None, backgroundColor: str | None = None, fansOnly: bool = False):
		"""
		Editing blog.

		**Parameters**:
		- blogId: str
		- title: str = None
		- content: str = None
		- imageList: list = None
		- categoriesList: list = True
		- backgroundColor: str = None
			- should be only hex code, like "#000000"
			- if None, it will be just white
		- fansOnly: bool = False
			- is it for your onlyfans or no?
			- works only if you have fanclub
		"""

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
		"""
		Deleting blog.

		**Parameters**:
		- blogId: str
		"""
		return self.req.request("DELETE", f"/x{self.comId}/s/blog/{blogId}")

	def delete_wiki(self, wikiId: str):
		"""
		Deleting wiki.

		**Parameters**:
		- wikiId: str
		"""
		return self.req.request("DELETE", f"/x{self.comId}/s/item/{wikiId}") 

	def repost_blog(self, content: str | None = None, blogId: str | None = None, wikiId: str | None = None):
		"""
		Reposing blog.

		**Parameters**
		- blogId: str = None
		- wikiId: str = None
			- can be only blogId or wikiId
			- blogId > wikiId
			- if both are None, it will raise Exception
		- content: str = None
		"""
		if blogId is None and wikiId is None: raise SpecifyType
		data = {
			"content": content,
			"refObjectId": blogId if blogId else wikiId,
			"refObjectType": 1 if blogId else 2,
			"type": 2,
		}

		return self.req.request("POST", f"/x{self.comId}/s/blog", data)

	def repair_check_in(self, repair_method: str = RepairMethod.Coins):
		"""
		Repairing check in streak.

		**Parameters**
		- method: int = RepairMethod.Coins
			- if ``amino.arguments.RepairMethod.Coins``, it will use coins
			- if ``amino.arguments.RepairMethod.AminoPlus``, it will use Amino+ superpower
		"""
		if repair_method not in RepairMethod.all: raise WrongType(repair_method)
		data = {
			"repairMethod": repair_method
		}

		return self.req.request("POST", f"/x{self.comId}/s/check-in/repair", data)


	def lottery(self, tz: int | None = None):
		"""
		Testing your luck in lottery. Once a day, of course.

		**Parameters**
		- tz: int 
			- better dont touch
		"""
		return self.req.request("POST", f"/x{self.comId}/s/check-in/lottery", { "timezone": tz if tz else timezone()})["lotteryLog"]

	def edit_profile(self, nickname: str | None = None, content: str | None = None, icon: BinaryIO | None = None, chatRequestPrivilege: str | None = None, imageList: list | None = None, captionList: list | None = None, backgroundImage: str | None = None, backgroundColor: str | None = None, titles: list | None = None, colors: list | None = None, defaultBubbleId: str | None = None):
		"""
		Edit account's Profile.

		**Parameters**
		- nickname : Nickname of the Profile.
		- content : Biography of the Profile.
		- icon : Icon of the Profile.
		- titles : Titles.
		- colors : Colors for titles.
		- imageList : List of images.
		- captionList : Captions for images.
		- backgroundImage : Url of the Background Picture of the Profile.
		- backgroundColor : Hexadecimal Background Color of the Profile.
		- defaultBubbleId : Chat bubble ID.
		- chatRequestPrivilege : Manage your right to accept chats.
		"""

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
		"""
		vote in the poll

		**Parameters**
		- optionId : ID of the poll option
		- blogId : ID of the Blog.
		"""

		data = {
			"value": 1,
			"eventSource": "PostDetailView"
		}
		return self.req.request("POST",  f"x{self.comId}/s/blog/{blogId}/poll/option/{optionId}/vote", data)


	def comment(self, message: str, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None, replyTo: str | None = None, isGuest: bool | None = False):
		"""
		Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- message : Message to be sent.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		- replyTo : ID of the Comment to Reply to.
		- isGuest : You want to be Guest or no?
		"""
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
						  
	def delete_comment(self, commentId: str, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None):
		"""
		Delete a Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- commentId : ID of the Comment.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
		if userId:url = f"/x{self.comId}/s/user-profile/{userId}/comment/{commentId}"
		elif blogId:url = f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}"
		elif wikiId:url = f"/x{self.comId}/s/item/{wikiId}/comment/{commentId}"
		else:raise SpecifyType

		return self.req.request("DELETE",  url)

	def like_blog(self, blogId: str | list | None = None, wikiId: str | None = None):
		"""
		Like a Blog, Multiple Blogs or a Wiki.

		**Parameters**
		- blogId : ID of the Blog or List of IDs of the Blogs. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
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

	def unlike_blog(self, blogId: str | None = None, wikiId: str | None = None):
		"""
		Remove a like from a Blog or Wiki.

		**Parameters**
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
		if blogId: url = f"/x{self.comId}/s/blog/{blogId}/vote?eventSource=UserProfileView"
		elif wikiId: url = f"/x{self.comId}/s/item/{wikiId}/vote?eventSource=PostDetailView"
		else: raise SpecifyType

		return self.req.request("DELETE",  url)

	def like_comment(self, commentId: str | None, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None):
		"""
		Like a Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- commentId : ID of the Comment.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
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

	def unlike_comment(self, commentId: str, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None):
		"""
		Remove a like from a Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- commentId : ID of the Comment.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
		if userId:url = f"/x{self.comId}/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView"
		elif blogId:url = f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		elif wikiId:url = f"/x{self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		else:raise SpecifyType

		return self.req.request("DELETE",  url)

	def upvote_comment(self, blogId: str, commentId: str):
		"""
		Upvote comment on question.

		**Parameters**
		- blogId : ID of the Blog.
		- commentId : ID of the Comment.
		"""
		data = {
			"value": 1,
			"eventSource": "PostDetailView"
		}

		return self.req.request("POST",  f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1", data)

	def downvote_comment(self, blogId: str, commentId: str):
		"""
		Downvote comment on question.

		**Parameters**
		- blogId : ID of the Blog.
		- commentId : ID of the Comment.
		"""
		data = {
			"value": -1,
			"eventSource": "PostDetailView"
		}

		return self.req.request("POST",  f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1", data)

	def unvote_comment(self, blogId: str, commentId: str):
		"""
		Remove vote from comment.

		**Parameters**
		- blogId : ID of the Blog.
		- commentId : ID of the Comment.
		"""
		return self.req.request("DELETE",  f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?eventSource=PostDetailView")

	def reply_wall(self, userId: str, commentId: str, message: str):
		"""
		Reply to comment on wall.

		**Parameters**
		- userId : ID of the User.
		- commentId : ID of the Comment.
		- message : Message.
		"""
		data = {
			"content": message,
			"stackedId": None,
			"respondTo": commentId,
			"type": 0,
			"eventSource": "UserProfileView"
		}

		return self.req.request("POST",  f"/x{self.comId}/s/user-profile/{userId}/comment", data)

	def send_active_obj(self, startTime: int | None = None, endTime: int | None = None, tz: int | None = None, timers: list | None = None):
		"""
		Sending mintues to Amino servers.

		**Parameters**
		- startTime : Unixtime (int) of start time.
		- endTime : Unixtime (int) of end time.
		- tz : Timezone.
		- timers : Timers instead startTime and endTime.
		"""
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
		"""
		Sets your activity status to offline or online.

		**Parameters**
		- status: bool
			- True: online
			- False: offline
		"""
		data = {
			"onlineStatus": 1 if status is True else 2,
			"duration": 86400
		}

		return self.req.request("POST",  f"/x{self.comId}/s/user-profile/{self.profile.userId}/online-status", data)

	def check_notifications(self):
		"""
		Checking notifications as read.
		"""
		return self.req.request("POST",  f"/x{self.comId}/s/notification/checked")

	def delete_notification(self, notificationId: str):
		"""
		Delete notification.

		**Parameters**:
		- notificationId: id of the notification
		"""
		return self.req.request("DELETE",  f"/x{self.comId}/s/notification/{notificationId}")

	def clear_notifications(self):
		"""
		Remove all notifications.
		"""
		return self.req.request("DELETE",  f"/x{self.comId}/s/notification")
	
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

	def invite_to_chat(self, userId: str | list | tuple, chatId: str):
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
		data = { "uids": userIds }

		return self.req.request("POST",  f"/x{self.comId}/s/chat/thread/{chatId}/member/invite", data)

	def add_to_favorites(self, userId: str):
		"""
		Adding user to favotites.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.request("POST",  f"/x{self.comId}/s/user-group/quick-access/{userId}")
	
	def send_coins(self, coins: int, blogId: str | None = None, chatId: str | None = None, objectId: str | None = None, transactionId: str | None = None):
		"""
		Sending coins.

		**Parameters**
		- coins : how many coins to send (in my opinion maximum 500 at a time)
		- blogId : ID of the Blog.
		- chatId : ID of the Chat.
		- objectId : ID of some object.
		- transactionId : ID of transaction (generated automatically)
		"""
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
		"""
		Thank you for the coins

		**Parameters**
		- chatId : ID of the Blog.
		- userId : ID of the Chat.
		"""
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users/{userId}/thank")

	def follow(self, userId: str | list):
		"""
		Follow an User or Multiple Users.

		**Parameters**
		- userId : ID of the User or List of IDs of the Users.
		"""
		
		if isinstance(userId, str):
			return self.req.request("POST", f"/x{self.comId}/s/user-profile/{userId}/member")
		elif isinstance(userId, list):
			data = { "targetUidList": userId }
			return self.req.request("POST", f"/x{self.comId}/s/user-profile/{self.userId}/joined", data)
		else: raise WrongType(f"userId: {type(userId)}")

	def unfollow(self, userId: str):
		"""
		Unfollow an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.request("DELETE", f"/x{self.comId}/s/user-profile/{self.userId}/joined/{userId}")

	def block(self, userId: str):
		"""
		Block an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.request("POST",  f"/x{self.comId}/s/block/{userId}")

	def unblock(self, userId: str):
		"""
		Unblock an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.request("DELETE",  f"/x{self.comId}/s/block/{userId}")


	def visit(self, userId: str):
		"""
		Visit an User

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.request("GET",  f"/x{self.comId}/s/user-profile/{userId}?action=visit")



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

	#from aminofixfix
	#idk, i don't test it
	def send_video(self, chatId: str, videoFile: BinaryIO, imageFile: BinaryIO, message: str | None = None, mediaUhqEnabled: bool = False):
		"""
		Sending video.

		**Parameters**
		- chatId: chat Id
		- message: message
		- videoFile: BinaryIO open(file, "rb") (video file)
		- imageFile: BinaryIO open(file, "rb") (image file)
		- mediaUhqEnabled: high quality?
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
			"type": MessageTypes.Video,
			"mediaUhqEnabled": mediaUhqEnabled,
			"extensions": {}    
		}

		files = {
			video: (video, videoFile.read(), 'video/mp4'),
			cover: (cover, imageFile.read(), 'application/octet-stream'),
			'payload': (None, data, 'application/octet-stream')
		}
		return self.req.request("POST",  f"/x{self.comId}/s/chat/thread/{chatId}/message", data, files=files, content_type=None)

	def send_message(self, chatId: str, message: str | None  = None, messageType: int = MessageTypes.Text, file: BinaryIO | None = None, replyTo: str | None = None, mentionUserIds: list | None = None, stickerId: str | None = None, embedId: str | None = None, embedType: int | None = None, embedLink: str | None = None, embedTitle: str | None = None, embedContent: str | None = None, embedImage: BinaryIO | None = None):
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
		- embedLink : Link of the Embed. Can be only "ndc://" link
		- embedImage : Image of the Embed. Required to send Embed, Can be only 1024x1024 max. Can be string to existing image uploaded to Amino or it can be opened (not readed) file.
		- embedId : ID of the Embed. Works only in AttachedObject Embeds. It can be any ID, just gen it using str_uuid4().
		- embedType : Type of the AttachedObject Embed. Works only in AttachedObject Embeds (use amino.AttachedObjectTypes. some)
		- embedTitle : Title of the Embed. Works only in AttachedObject Embeds. Can be empty.
		- embedContent : Content of the Embed. Works only in AttachedObject Embeds. Can be empty.
		"""		
		
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
		"""
		send full embed
		**Parameters**
		- message : Message to be sent
		- chatId : ID of the Chat.
		- link : Link of the Embed. Can be only "ndc://" link
		- image : Image of the Embed. Required to send Embed, Can be only 1024x1024 max. Can be string to existing image uploaded to Amino or it can be opened (not readed) file.
		"""
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
			return self.req.request("POST",  f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}/admin", data)
		return self.req.request("DELETE",  f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}")

	def mark_as_read(self, chatId: str, messageId: str):
		"""
		Mark a Message from a Chat as Read.

		**Parameters**
		- messageId : ID of the Message.
		- chatId : ID of the Chat.
		"""
		data = {"messageId": messageId}
		return self.req.request("POST",  f"/x{self.comId}/s/chat/thread/{chatId}/mark-as-read", data)

	def edit_chat(self, chatId: str, title: str | None = None, icon: str | None = None, content: str | None = None, announcement: str | None = None, keywords: list | None = None, pinAnnouncement: bool | None = None, publishToGlobal: bool | None = None, fansOnly: bool | None = None):
		"""
		Edit chat settings.

		**Parameters**
		- chatId : ID of the Chat.
		- title : Title of the Chat.
		- content : Content of the Chat.
		- icon : Icon of the Chat.
		- announcement : Announcement of the Chat.
		- pinAnnouncement : If the Chat Announcement should Pinned or not.
		- keywords : List of Keywords of the Chat.
		- publishToGlobal** : If the Chat should show on Public Chats or not.
		- fansOnly : If the Chat should be Fans Only or not.
		"""

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
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.userId}/alert", data)

	def pin_chat(self, chatId: str, pin: bool = True):
		"""
		Pin chat

		**Parameters**
		- chatId : id of the chat
		- pin : If the Chat should Pinned or not.
		"""
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}{'pin' if pin else 'unpin'}", {})


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
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.userId}/background", data)
	
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
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/co-host", data)


	def delete_co_host(self, chatId: str, userId: str):
		"""
		Remove co-host from chat
		**Parameters**:
		- chatId: id of the chat 
		- userId: id of the user 
		"""
		return self.req.request("DELETE", f"/x{self.comId}/chat/thread/{chatId}/co-host/{userId}")


	def chat_view_only(self, chatId: str, viewOnly: bool = False):
		"""
		set view-only mode

		**Parameters**
		- chatId : id of the chat
		- viewOnly : enable view only mode?
		"""
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/view-only/{'enable' if viewOnly else 'disable'}")
	
	def member_can_invite_to_chat(self, chatId: str, canInvite: bool = True):
		"""
		permission to invite users to chat

		**Parameters**
		- chatId : id of the chat
		- canInvite : member can invite to chat ?.
		"""
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/members-can-invite/{'enable' if canInvite else 'disable'}")

	def member_can_chat_tip(self, chatId: str, canTip: bool = True):
		"""
		permission to tip chat

		**Parameters**
		- chatId : id of the chat
		- canTip : if the Chat should be Tippable or not.
		"""
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/tipping-perm-status/{'enable' if canTip else 'disable'}")

	def transfer_host(self, chatId: str, userIds: list[str]):
		"""
		transfer host from chat

		**Parameters**:
		- chatId: id of the chat 
		- userIds: id of the user's
		"""
		data = { "uidList": userIds }
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer", data)

	def accept_host(self, chatId: str, requestId: str):
		"""
		Accepting host in chat.

		**Parameters**:
		- chatId: id of the chat 
		- requestId: host transfer request ID
		"""
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept")

	def kick(self, userId: str, chatId: str, allowRejoin: bool = True):
		return self.req.request("DELETE", f"/x{self.comId}/s/chat/thread/{chatId}/member/{userId}?allowRejoin={int(allowRejoin)}")

	def join_chat(self, chatId: str):
		"""
		Join an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.userId}")

	def leave_chat(self, chatId: str):
		"""
		Leave an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return self.req.request("DELETE", f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.userId}")

	def delete_chat(self, chatId: str):
		"""
		Delete a Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return self.req.request("DELETE", f"/x{self.comId}/s/chat/thread/{chatId}")

	def subscribe_influencer(self, userId: str, autoRenew: str = False, transactionId: str | None = None):
		"""
		Subscibing to VIP person.

		**Parameters**
		- userId: str
			- id of object that you wanna buy
		- isAutoRenew: bool = False
			- do you wanna auto renew your subscription?
		- transactionId: str = None
			- unique id of transaction
		"""
		
		data = {
			"paymentContext": {
				"transactionId": transactionId if transactionId else str(uuid4()),
				"isAutoRenew": autoRenew
			}
		}
		return self.req.request("POST", f"/x{self.comId}/s/influencer/{userId}/subscribe", data)

	def promotion(self, noticeId: str, type: str = PromotionTypes.Accept):
		"""
		Accept or deny promotion to curator/leader/agent.

		**Parameters**:
		- noticeId
			- get from `get_notices`
		- type: accept or deny
		"""
		return self.req.request("POST", f"/x{self.comId}/s/notice/{noticeId}/{type}")

	def play_quiz_raw(self, quizId: str, quizAnswerList: list, quizMode: int = QuizMode.NormalMode):
		"""
		Send quiz results.

		**Parameters**
		- quizId:  id of quiz
		- quizAnswerList: answer list
		- quizMode: quiz mode
			- hellMode: 1
			- default: 0
		"""
		data = {
			"mode": quizMode,
			"quizAnswerList": quizAnswerList
		}

		return self.req.request("POST", f"/x{self.comId}/s/blog/{quizId}/quiz/result", data)

	def play_quiz(self, quizId: str, questionIdsList: list, answerIdsList: list, quizMode: int = QuizMode.NormalMode):
		"""
		Send quiz results.

		**Parameters**
		- quizId:  id of quiz
		- quizAnswerList: answer list
		- quizMode: quiz mode
			- hellMode: 1
			- default: 0
		"""
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
		"""
		Manage permissions to VC.

		**Parameters**
		- chatId: chat ID
		- permission: voice chat access (use ``amino.arguments.VoiceChatJoinPermissions. some``)
		"""
		data = { "vvChatJoinType": permission }
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/vvchat-permission", data)

	def get_vc_reputation_info(self, chatId: str):
		"""
		Get info about reputation that you got from VC.

		**Parameters**
		- chatId: chat ID
		"""
		return self.req.request("GET", f"/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation")

	def claim_vc_reputation(self, chatId: str):
		"""
		Claim reputation that you got from VC.

		**Parameters**
		- chatId: chat ID
		"""
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation")

	def get_all_users(self, type: str = UsersTypes.Recent, start: int = 0, size: int = 25):
		"""
		Get info about all members.

		**Parameters**
		- type: str
			- use ``amino.arguments.UsersTypes``
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		if type not in UsersTypes.all:raise WrongType(f"type: {type} not in {UsersTypes.all}")
		return self.req.request("GET", f"/x{self.comId}/s/user-profile?type={type}&start={start}&size={size}")

	def get_online_users(self, start: int = 0, size: int = 25):
		"""
		Get info about all online members.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/live-layer?topic=ndtopic:x{self.comId}:online-members&start={start}&size={size}")

	def get_online_favorite_users(self, start: int = 0, size: int = 25):
		"""
		Get info about all online favorite members.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/user-group/quick-access?type=online&start={start}&size={size}")

	def get_user_info(self, userId: str):
		"""
		Information of an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/user-profile/{userId}")["userProfile"]

	def get_user_following(self, userId: str, start: int = 0, size: int = 25):
		"""
		List of Users that the User is Following.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/user-profile/{userId}/joined?start={start}&size={size}")["userProfileList"]

	def get_user_followers(self, userId: str, start: int = 0, size: int = 25):
		"""
		List of Users that are Following the User.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/user-profile/{userId}/member?start={start}&size={size}")["userProfileList"]

	def get_user_checkins(self, userId: str, tz: int | None = None):
		"""
		Get info about user's check ins.

		**Parameters**
		- userId: user id
		- tz: time zone
		"""
		return self.req.request("GET", f"/x{self.comId}/s/check-in/stats/{userId}?timezone={tz if tz else timezone()}")


	def get_user_visitors(self, userId: str, start: int = 0, size: int = 25):
		"""
		List of Users that Visited the User.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/user-profile/{userId}/visitors?start={start}&size={size}")

	def get_user_blogs(self, userId: str, start: int = 0, size: int = 25):
		"""
		Get info about user's blogs.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/blog?type=user&q={userId}&start={start}&size={size}")["blogList"]

	def get_user_wikis(self, userId: str, start: int = 0, size: int = 25):
		"""
		Get info about user's wikis.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/item?type=user-all&start={start}&size={size}&cv=1.2&uid={userId}")["itemList"]

	def get_user_achievements(self, userId: str):
		"""
		Get info about user's achievements.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/user-profile/{userId}/achievements")["achievements"]

	def get_influencer_fans(self, userId: str, start: int = 0, size: int = 25):
		"""
		Get all who subscribed to fanclub.

		**Parameters**:
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/influencer/{userId}/fans?start={start}&size={size}")

	def get_blocked_users(self, start: int = 0, size: int = 25):
		"""
		List of Users that the User Blocked.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.

		"""
		return self.req.request("GET", f"/x{self.comId}/s/block?start={start}&size={size}")["userProfileList"]

	def get_blocker_users(self, start: int = 0, size: int = 25):
		"""
		List of Users that are Blocking the User.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/block?start={start}&size={size}")["blockerUidList"]

	def search_users(self, nickname: str, start: int = 0, size: int = 25):
		"""
		Searching users by nickname.

		**Parameters**
		- nickname : user nickname
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/user-profile?type=name&q={nickname}&start={start}&size={size}")["userProfileList"]

	def get_saved_blogs(self, start: int = 0, size: int = 25):
		"""
		Recieve all your saved blogs.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/bookmark?start={start}&size={size}")["bookmarkList"]

	def get_leaderboard_info(self, type: str = LeaderboardTypes.Day, start: int = 0, size: int = 25):
		"""
		Recieve all your users from leaderboard.

		**Parameters**
		- type: leaderboard type (use ``amino.arguments.LeaderboardTypes``)
		- start : Where to start the list.
		- size : Size of the list.
		"""
		if type not in LeaderboardTypes.all:raise WrongType(f"LeaderboardTypes.all: {type} not in {LeaderboardTypes.all}")
		url = f"/g/s-x{self.comId}/community/leaderboard?rankingType={type}&start={start}"
		if type != 4:url += f"&size={size}"

		return self.req.request("GET", url)["userProfileList"]


	def get_wiki_info(self, wikiId: str):
		"""
		Get all things about wiki post.

		**Parameters**
		- wikiId: wiki id
		"""
		return self.req.request("GET", f"/x{self.comId}/s/item/{wikiId}")

	def get_recent_wiki_items(self, start: int = 0, size: int = 25):
		"""
		Get all recent wiki items.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/item?type=catalog-all&start={start}&size={size}")["itemList"]

	def get_wiki_categories(self, start: int = 0, size: int = 25):
		"""
		Get all wiki categories.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/item-category?start={start}&size={size}")["itemCategoryList"]

	def get_wiki_category(self, categoryId: str, start: int = 0, size: int = 25):
		"""
		Get all wiki from category.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		- categoryId : wiki category Id
		"""
		return self.req.request("GET", f"/x{self.comId}/s/item-category/{categoryId}?pagingType=t&start={start}&size={size}")

	def get_tipped_users(self, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None, chatId: str | None = None, start: int = 0, size: int = 25):
		"""
		Get all users who tipped on your posting.

		**Parameters**
		- blogId: blog Id
		- wikiId: wiki Id
		- quizId: quiz Id
		- fileId: file Id
		- chatId: chat Id
			- can be only one field
		- start : Where to start the list.
		- size : Size of the list.
		"""
		object_types = {
			'blogId': {'id': blogId or quizId, 'url': f"/x{self.comId}/s/blog/{blogId or quizId}/tipping/tipped-users-summary"},
			'wikiId': {'id': wikiId, 'url': f"/x{self.comId}/s/item/{wikiId}/tipping/tipped-users-summary"},
			'chatId': {'id': chatId, 'url': f"/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users-summary"},
			'fileId': {'id': fileId, 'url': f"/x{self.comId}/s/shared-folder/files/{fileId}/tipping/tipped-users-summary"}
		}
		for key, value in object_types.items():
			if value['id']:return self.req.request("GET", f"{value['url']}?start={start}&size={size}")
		else:raise SpecifyType


	def get_my_chats(self, start: int = 0, size: int = 25):
		"""
		List of Chats the account is in.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/chat/thread?type=joined-me&start={start}&size={size}")["threadList"]

	def get_public_chats(self, type: str = Sorting2.Recommended, start: int = 0, size: int = 25):
		"""
		List of Public Chats of the Community.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		- type : filter chats by type. use ``Sorting2`` object
		"""
		return self.req.request("GET", f"/x{self.comId}/s/chat/thread?type=public-all&filterType={type}&start={start}&size={size}")["threadList"]

	def get_chat(self, chatId: str):
		"""
		Get the Chat Object from an Chat ID.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/chat/thread/{chatId}")["thread"]

	def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str | None = None):
		"""
		List of Messages from an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		- size : Size of the list.
		- pageToken : Next Page Token.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}{f'&pageToken={pageToken}' if pageToken else  ''}")

	def get_message_info(self, chatId: str, messageId: str):
		"""
		Information of an Message from an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		- message : ID of the Message.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}")["message"]

	def get_blog_info(self, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None):
		"""
		Get all info about posting.

		**Parameters**
		- blogId: blog id
		- wikiId: wiki id
		- quizId: quiz id
		- fileId: file id
			- can be only one field
		"""
		if blogId or quizId:
			return self.req.request("GET", f"/x{self.comId}/s/blog/{blogId or quizId}")
		elif wikiId:
			return self.req.request("GET", f"/x{self.comId}/s/item/{wikiId}")
		elif fileId:
			return self.req.request("GET", f"/x{self.comId}/s/shared-folder/files/{fileId}")["file"]
		raise SpecifyType

	def get_blog_comments(self, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None, sorting: str = Sorting.Newest, start: int = 0, size: int = 25):
		"""
		Get all blog comments.

		**Parameters**
		- blogId: blog id
		- wikiId: wiki id
		- quizId: quiz id
		- fileId: file id
			- can be only one field
		- start : Where to start the list.
		- size : Size of the list.
		- sorting : sorting comments (use ``amino.arguments.Sorting. some``)
		"""
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
		"""
		Get all possible blog categories.

		**Parameters**
		- size: how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/blog-category?size={size}")["blogCategoryList"]

	def get_blogs_by_category(self, categoryId: str,start: int = 0, size: int = 25):
		"""
		Get all possible blogs in category.

		**Parameters**:
		- categoryId: category Id
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/blog-category/{categoryId}/blog-list?start={start}&size={size}")["blogList"]

	def get_quiz_rankings(self, quizId: str, start: int = 0, size: int = 25):
		"""
		Get quiz winners.

		**Parameters**:
		- quizId: quiz Id
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/blog/{quizId}/quiz/result?start={start}&size={size}")

	def get_wall_comments(self, userId: str, sorting: str = Sorting.Newest, start: int = 0, size: int = 25):
		"""
		List of Wall Comments of an User.

		**Parameters**
		- userId: user id
		- start : Where to start the list.
		- size : Size of the list.
		- sorting : sorting comments (use ``amino.arguments.Sorting. some``)
		"""
		if sorting not in Sorting.all:raise ValueError(f"Sorting.all: {sorting} not in {Sorting.all}")
		return self.req.request("GET", f"/x{self.comId}/s/user-profile/{userId}/comment?sort={sorting}&start={start}&size={size}")["commentList"]

	def get_recent_blogs(self, pageToken: str | None = None, start: int = 0, size: int = 25):
		"""
		Get recent blogs.

		**Parameters**
		- size : Size of the list.
		- start : start pos
		- pageToken : Next Page Token.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/feed/blog-all?pagingType=t&size={size}{f'&pageToken={pageToken}' if pageToken else  f'&start={start}'}")

	def get_chat_users(self, chatId: str, start: int = 0, size: int = 25):
		"""
		Getting users in chat.

		**Parameters**
		- chatId: chat id
		- start: int
			- start pos
		- size: int
			- how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/chat/thread/{chatId}/member?type=default&cv=1.2&start={start}&size={size}")["memberList"]

	def get_notifications(self, start: int = 0, size: int = 25):
		"""
		Getting notifications in community.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/notification?pagingType=t&start={start}&size={size}")["notificationList"]

	def get_notices(self, start: int = 0, size: int = 25):
		"""
		Getting notices in community.

		Notices are NOT notifications. Its like "you are in read only mode", "you got strike", "you got warning", "somebody wants to promote you to curator/leader/curator".

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/notice?type=usersV2&status=1&start={start}&size={size}")["noticeList"]

	def get_sticker_pack_info(self, sticker_pack_id: str):
		"""
		Getting all info about sticker pack.

		**Parameters**
		- sticker_pack_id: id of the sticker pack
		"""
		return self.req.request("GET", f"/x{self.comId}/s/sticker-collection/{sticker_pack_id}?includeStickers=true")["stickerCollection"]

	def get_my_sticker_packs(self):
		"""
		Getting sticker packs in account.

		**Parameters**
		- sticker_pack_id: id of the sticker pack
		"""
		return self.req.request("GET", f"/x{self.comId}/s/sticker-collection?includeStickers=false&type=my-active-collection")["stickerCollection"]

	def get_store_chat_bubbles(self, start: int = 0, size: int = 25):
		"""
		Getting all available chat bubbles from store.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/store/items?sectionGroupId=chat-bubble&start={start}&size={size}")
	
	def get_store_stickers(self, start: int = 0, size: int = 25):
		"""
		Getting all available stickers from store.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/store/items?sectionGroupId=sticker&start={start}&size={size}")

	def get_community_stickers(self):
		"""
		Getting all available stickers in community.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/sticker-collection?type=community-shared")

	def get_sticker_collection(self, collectionId: str):
		"""
		Getting all available info about sticker pack.

		**Parameters**
		- collectionId: id of the collection
		"""
		return self.req.request("GET", f"/x{self.comId}/s/sticker-collection/{collectionId}?includeStickers=true")["stickerCollection"]

	def get_shared_folder_info(self):
		"""
		Getting all available info about shared folder.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/shared-folder/stats")["stats"]

	def get_shared_folder_files(self, type: str = Sorting2.Latest, start: int = 0, size: int = 25):
		"""
		Getting all available files in shared folder.

		**Parameters**
		- type: str = "latest"
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/shared-folder/files?type={type}&start={start}&size={size}")["fileList"]

	#
	# MODERATION MENU
	#

	def moderation_history(self, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None, size: int = 25):
		"""
		Getting moderation history of object.

		**Parameters**
		- userId: user Id
		- blogId: blog Id
		- wikiId: wiki Id
		- quizId: quiz Id
		- fileId: file Id
			- can be only one field
			- if all fields are None, getting all latest operations in "shared" moderation history
		- size: int = 25
			- how much you want to get
		"""
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

	def feature(self, days: int = FeatureDays.ONE_DAY, userId: str | None = None, chatId: str | None = None, blogId: str | None = None, wikiId: str | None = None):
		"""
		Feature object.

		**Parameters**
		- days: feature days
		- userId: user Id
		- blogId: blog Id
		- wikiId: wiki Id
		- quizId: quiz Id
			- can be only one field
		"""
		times = {
			"chatId": {
				1: 3600,
				2: 7200,
				3: 10800
			},
			"ect": {
				1: 86400,
				2: 172800,
				3: 259200,
			}
		}
		if days not in times[chatId].keys(): raise WrongType(days)

		data = {
			"adminOpName": 114,
			"adminOpValue": {
				"featuredDuration": times["chatId" if chatId else "ect"][days]
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

	def unfeature(self, userId: str | None = None, chatId: str | None = None, blogId: str | None = None, wikiId: str | None = None):
		"""
		Unfeature object.

		**Parameters**
		- userId: user Id
		- blogId: blog Id
		- wikiId: wiki Id
		- quizId: quiz Id
			- can be only one field
		"""
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

	def hide(self, userId: str | None = None, chatId: str | None = None, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None, reason: str | None = None):
		"""
		Hide object.

		**Parameters**
		- userId: user Id
		- blogId: blog Id
		- wikiId: wiki Id
		- quizId: quiz Id
		- fileId: file Id
			- can be only one field
		- reason: hide reason
		"""
		
		data = {
			"adminOpName": 110,
			"adminOpNote": {
				"content": reason,
			}
		}
		if userId is None:
			data["adminOpValue"] = 9

		if userId:
			data["adminOpName"] = 18
			url = f"/x{self.comId}/s/user-profile/{userId}/admin"
		elif blogId:
			url = f"/x{self.comId}/s/blog/{blogId}/admin"
		elif quizId:
			url = f"/x{self.comId}/s/blog/{quizId}/admin"
		elif wikiId:
			url = f"/x{self.comId}/s/item/{wikiId}/admin"
		elif chatId:
			url = f"/x{self.comId}/s/chat/thread/{chatId}/admin"
		elif fileId:
			url = f"/x{self.comId}/s/shared-folder/files/{fileId}/admin"
		else: raise SpecifyType

		return self.req.request("POST", url, data)

	def unhide(self, userId: str | None = None, chatId: str | None = None, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None, reason: str | None = None):
		"""
		unhide object.

		**Parameters**
		- userId: user Id
		- blogId: blog Id
		- wikiId: wiki Id
		- quizId: quiz Id
		- fileId: file Id
			- can be only one field
		- reason: unhide reason
		"""

		data = {
			"adminOpName": 110,
			"adminOpNote": {
				"content": reason
			}
		}
		if userId is None:
			data["adminOpValue"] = 0

		if userId:
			data["adminOpName"] = 19
			url = f"/x{self.comId}/s/user-profile/{userId}/admin"
		elif blogId:
			url = f"/x{self.comId}/s/blog/{blogId}/admin"
		elif quizId:
			url = f"/x{self.comId}/s/blog/{quizId}/admin"
		elif wikiId:
			url = f"/x{self.comId}/s/item/{wikiId}/admin"
		elif chatId:
			url = f"/x{self.comId}/s/chat/thread/{chatId}/admin"
		elif fileId:
			url = f"/x{self.comId}/s/shared-folder/files/{fileId}/admin"
		else: raise SpecifyType

		return self.req.request("POST", url, data)

	def edit_titles(self, userId: str, titles: list[dict]):
		"""
		Edit user's titles.

		**Parameters**
		- userId: user id
		- titles: list of titles

		- example: 
		[
			{"title": "#00FF00"},
			{"cute girl": "#FFC0CB"}
		]

		titles = [{"title name": "title color"}]
		"""

		tlt = list()
		for title  in titles:
			for title, color in title.items():
				tlt.append(
					{"title": title, "color": color}
				)
		data = {
			"adminOpName": 207,
			"adminOpValue": {
				"titles": tlt
			}
		}

		return self.req.request("POST", f"/x{self.comId}/s/user-profile/{userId}/admin", data)

	
	def warn(self, userId: str, reason: str = None):
		"""
		Give a warn to user.

		**Parameters**
		- userId: user Id
		- reason: warn reason
		"""
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


	def get_strike_templates(self):
		"""
		get strike templates
		"""
		return self.req.request("GET", f"/x{self.comId}/s/notice/message-template/strike")

	def get_warn_templates(self):
		"""
		get warn templates
		"""
		return self.req.request("GET", f"/x{self.comId}/s/notice/message-template/warning")


	def strike(self, userId: str, time: int = StrikeTime.ONE_HOUR, title: str = None, reason: str = None):
		"""
		Give a strike (warn + read only mode) to user.

		**Parameters**
		- userId: str
		- title: strike title
		- reason: strike reason
		- time: 
			- time == 1 is 1 hour
			- time == 2 is 3 hours
			- time == 3 is 6 hours
			- time == 4 is 12 hours
			- time == 5 is 24 hours
				- use ``amino.arguments.StrikeTime``
		"""

		times = {
			1: 86400,
			2: 10800,
			3: 21600,
			4: 43200,
			5: 86400
		}
		if time not in times.keys():raise WrongType(time)

		data = {
			"uid": userId,
			"title": title,
			"content": reason,
			"attachedObject": {
				"objectId": userId,
				"objectType": 0
			},
			"penaltyType": 1,
			"penaltyValue": times[time],
			"adminOpNote": {},
			"noticeType": 4
		}
		return self.req.request("POST", f"/x{self.comId}/s/notice", data)

	def ban(self, userId: str, reason: str | None = None, banType: int | None = None):
		"""
		Ban user.

		**Parameters**
		- userId: user Id
		- reason: ban reason
		- banType: ban type (idk)
		"""
		data = {
			"reasonType": banType,
			"note": {
				"content": reason if reason else "No reason provided. (powered by amino.api)"
			}
		}
		return self.req.request("POST", f"/x{self.comId}/s/user-profile/{userId}/ban", data)

	def unban(self, userId: str, reason: str | None = None):
		"""
		Unban user.

		**Parameters**
		- userId: user Id
		- reason: unban reason
		"""
		data = {
			"note": {
				"content": reason if reason else "No reason provided. (powered by amino.api)"
			}
		}

		return self.req.request("POST", f"/x{self.comId}/s/user-profile/{userId}/unban", data)

	def reorder_featured_users(self, userIds: list[str]):
		"""
		Reorder featured users.

		**Parameters**
		- userIds: list with user id's 
		"""
		data = { "uidList": userIds }
		return self.req.request("POST", f"/x{self.comId}/s/user-profile/featured/reorder", data)

	def get_hidden_blogs(self, start: int = 0, size: int = 25):
		"""
		Get hidden blogs.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/feed/blog-disabled?start={start}&size={size}")["blogList"]
	

	def get_featured_users(self, start: int = 0, size: int = 25):
		"""
		Get featured users.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/user-profile?type=featured&start={start}&size={size}")

	def review_quiz_questions(self, quizId: str):
		"""
		Review quiz questions.

		**Parameters**
		- quizId: quiz Id
		"""
		return self.req.request("GET", f"/x{self.comId}/s/blog/{quizId}?action=review")["blog"]["quizQuestionList"]

	def get_recent_quiz(self, start: int = 0, size: int = 25):
		"""
		Get recent quizes.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/blog?type=quizzes-recent&start={start}&size={size}")["blogList"]

	def get_trending_quiz(self, start: int = 0, size: int = 25):
		"""
		Get tranding quizes.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/feed/quiz-trending?start={start}&size={size}")["blogList"]

	def get_best_quiz(self, start: int = 0, size: int = 25):
		"""
		Get the best quizes ever.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/feed/quiz-best-quizzes?start={start}&size={size}")["blogList"]


	def purchase(self, objectId: str, objectType: int = PurchaseTypes.Bubble, aminoPlus: bool = True, autoRenew: bool = False):
		"""
		Purchasing something from store

		**Parameters**
		- objectId: id of object that you wanna buy
		- objectType: type of object that you wanna buy
			- use ``amino.arguments.PurchaseTypes. some``
		- aminoPlus: is amino+ object?
		- isAutoRenew:  do you wanna auto renew your purchase?
		"""
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
		"""
		Apply avatar frame.

		**Parameters**
		- avatarId : ID of the avatar frame.
		- applyToAll : Apply to all.
		"""
		data = {
			"frameId": avatarId,
			"applyToAll": 1 if applyToAll is True else 0,
		}
		return self.req.request("POST", f"/x{self.comId}/s/avatar-frame/apply", data)

	def invite_to_vc(self, chatId: str, userId: str):
		"""
		Invite a User to a Voice Chat

		**Parameters**
		- chatId - ID of the Chat
		- userId - ID of the User
		"""
		data = { "uid": userId }
		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/vvchat-presenter/invite/", data)

	def add_poll_option(self, blogId: str, question: str):
		"""
		Add poll option.

		**Parameters**
		- blogId: blog Id
		- question: question
		"""

		data = {
			"mediaList": None,
			"title": question,
			"type": 0
		}
		return self.req.request("POST", f"/x{self.comId}/s/blog/{blogId}/poll/option", data)

	def create_wiki_category(self, title: str, parentCategoryId: str, content: str | None = None, media: list | None = None):
		"""
		Create wiki category.

		**Parameters**
		- title: category title
		- parentCategoryId: parent category id
		- content: text
		- media: media list
			- idk, looks like a trash. i will remake it.
		"""
		data = {
			"icon": None,
			"content": content,
			"label": title,
			"mediaList": media,
			"parentCategoryId": parentCategoryId,
		}
		return self.req.request("POST", f"/x{self.comId}/s/item-category", data)
		
	def create_shared_folder(self,title: str):
		"""
		Create shared folder.

		**Parameters**
		- title: folder title
		"""
		data = { "title": title }
		return self.req.request("POST", f"/x{self.comId}/s/shared-folder/folders", data)

	def submit_to_wiki(self, wikiId: str, message: str):
		"""
		Submit wiki to curator review.

		**Parameters**
		- wikiId: wiki id
		- message: text 
		"""
		
		data = {
			"message": message,
			"itemId": wikiId
		}
		return self.req.request("POST", f"/x{self.comId}/s/knowledge-base-request", data)

	def accept_wiki_request(self, requestId: str, destinationCategoryIdList: list):
		"""
		Accept wiki.

		**Parameters**
		- requestId: request Id
		- destinationCategoryIdList: Category id List
		"""
		data = {
			"destinationCategoryIdList": destinationCategoryIdList,
			"actionType": "create"
		}

		return self.req.request("POST", f"/x{self.comId}/s/knowledge-base-request/{requestId}/approve", data)

	def reject_wiki_request(self, requestId: str):
		"""
		Reject wiki.

		**Parameters**
		- requestId: request Id
		"""
		data = {}
		return self.req.request("POST", f"/x{self.comId}/s/knowledge-base-request/{requestId}/reject", data)

	def get_wiki_submissions(self, start: int = 0, size: int = 25):
		"""
		Get wiki submissions to be approved.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/knowledge-base-request?type=all&start={start}&size={size}")["knowledgeBaseRequestList"]

	def get_live_layer(self):
		"""
		Get live layer.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/live-layer/homepage?v=2")["liveLayerList"]

	def apply_bubble(self, bubbleId: str, chatId: str, applyToAll: bool = False):

		"""
		Apply bubble that you want.

		**Parameters**
		- bubbleId: bubble Id
		- chatId: chat Id
		- applyToAll: apply bubble to all chats?
		"""

		data = {
			"applyToAll": 1 if applyToAll is True else 0,
			"bubbleId": bubbleId,
			"threadId": chatId,
		}

		return self.req.request("POST", f"/x{self.comId}/s/chat/thread/apply-bubble", data)
		

	"""
	ACM
	"""

	def create_community(self, name: str, tagline: str, icon: BinaryIO, themeColor: str, joinType: int = CommunityJoinTypes.Open, primaryLanguage: str = "en"):
		"""
		Creating community.

		Accepting:
		- name: community name
		- tagline: community tagline
		- icon: icon
		- themeColor: color
		- joinType: use ``amino.arguments.CommunityJoinTypes. some``
			- 0 is open
			- 1 is semi-closed (you can request to be added in community)
			- 2 is fully closed (UNAVAILABLE AT ALL FOR ALL APPROVED COMMUNITIES)
		- primaryLanguage: community language
		"""
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
		"""
		This method can be used for getting info about current themepack of community.
		"""
		return self.req.request("POST", f"/g/s-x{self.comId}/community/info?withTopicList=1&withInfluencerList=1&influencerListOrderStrategy=fansCount")['community']['themePack']

	def upload_themepack(self, file: BinaryIO):
		"""
		Uploading new themepack.

		File is technically a ZIP file, but you should rename .zip to .ndthemepack.
		Also this "zip" file have specific stucture.

		The structure is:
		- theme_info.json
		- images/
			- background/
				- background_375x667.jpeg
				- background_750x1334.jpeg
			- logo/
				- logo_219x44.png
				- logo_439x88.png
			- titlebar/
				- titlebar_320x64.jpeg
				- titlebar_640x128.jpeg
			- titlebarBackground/
				- titlebarBackground_375x667.jpeg
				- titlebarBackground_750x1334.jpeg
		
		And now its time to explain tricky "theme.json".
		
		- I can't really explain "id" here, *maybe* its random uuid4.
		- "format-version" **SHOULD** be "1.0", its themepack format version
		- "author" is.. nickname or aminoId of theme uploader (or agent, it doesnt matter)
		- "revision".. u *can* leave revision that you have, Amino will do all stuff instead of you
		- "theme-color" should be **VALID** hex color. I think they didn't fixed that you can pass invalid hex color, but it will cost a crash on every device
		
		About images in "theme.json":

		- for logo folder stands key "logo" in json, for titlebar - "titlebar-image", for titlebarBackground - "titlebar-background-image", for background - "background-image"
		- you can *pass* or *not pass* these keys in json, if they are not passed they will ignored/deleted
		- keys have array values like this:
			- [
				{
					"height": height*2,
					"path": "images/logo/logo_width*2xheight*2.png",
					"width": width*2,
					"x": 0,
					"y": 0
				},
				{
					"height": height,
					"path": "images/logo/logo_widthxheight.png",
					"width": width,
					"x": 0,
					"y": 0
				}
			]
		- default values of height (h) and width (w) for every key:
			- "background-image":
				- w = 375
				- h = 667
			- "logo":
				- w = 196
				- h = 44
			- "titlebar-background-image":
				- w = 375
				- h = 667
			- "titlebar-image":
				- w = 320
				- h = 64
		- you *can* specify "x" and "y" if you want
		- theoretically you can provide different "w" and "h"

		**Parameters**
		- file: zip file (rename .zip to .ndthemepack)
		"""
		return self.req.request("POST", f"/x{self.comId}/s/media/upload/target/community-theme-pack", data=file.read())

	def delete_community(self, email: str, password: str, verificationCode: str):
		"""
		Deleting community.

		**Parameters**
		- email: agent email
		- password: agent password
		- verificationCode: email verification code
		"""
		
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
		"""
		Getting all communities where you are leader.

		**Parameters**
		- start: start pos
		- size: how much you want to get
		"""
		return self.req.request("GET", f"/g/s/community/managed?start={start}&size={size}")["communityList"]

	def get_categories(self, start: int = 0, size: int = 25):
		"""
		Getting categories of communities.

		**Parameters**
		- start: start pos
		- size: how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/blog-category?start={start}&size={size}")

	def change_sidepanel_color(self, color: str):
		"""
		Change sidepanel color.

		**Parameters**
		- color: should be hex color like "#123ABC"
		"""
		data = {
			"path": "appearance.leftSidePanel.style.iconColor",
			"value": color
		}
		return self.req.request("POST", f"/x{self.comId}/s/community/configuration", data)

	def promote(self, userId: str, rank: str):
		"""
		Promote user to curator, leader or agent.

		**Parameters**
		- userId: user Id
		- rank: can be only "agent"/"transfer-agent", "leader" or "curator"
			- use ``amino.arguments.AdministratorsRank. some``
		"""
		if rank not in AdministratorsRank.all:raise SpecifyType(f"[AdministratorsRank.all] -> Available ranks: {AdministratorsRank.all}")
		rank = rank.lower().replace("agent", "transfer-agent")
		return self.req.request("POST", f"/x{self.comId}/s/user-profile/{userId}/{rank}")

	def get_join_requests(self, start: int = 0, size: int = 25):
		"""
		Get all requests to join your community.

		**Parameters**
		- start: start pos
		- size: how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/community/membership-request?status=pending&start={start}&size={size}")
	
	def accept_join_request(self, userId: str):
		"""
		Accept user to join your community.

		**Parameters**
		- user Id: str
		"""
		data = {}
		return self.req.request("POST", f"/x{self.comId}/s/community/membership-request/{userId}/accept", data)
	
	def reject_join_request(self, userId: str):
		"""
		Reject user to join your community.

		**Parameters**
		- userId: user id
		"""
		data = {}
		return self.req.request("POST", f"/x{self.comId}/s/community/membership-request/{userId}/reject", data)

	def get_community_stats(self):
		"""
		Get community statistics.
		"""
		return self.req.request("GET", f"/x{self.comId}/s/community/stats")["communityStats"]

	def get_community_moderation_stats(self, type: str = "leader", start: int = 0, size: int = 25):
		"""
		Get community moderation statistics.

		**Parameters**
		- type: can be only "leader" or "curator"
		- start: start pos
		- size: how much you want to get
		"""
		if type.lower() not in ("leader", "curator"):raise WrongType(f"{type} not in ('leader', 'curator')")
		return self.req.request("GET", f"/x{self.comId}/s/community/stats/moderation?type={type.lower()}&start={start}&size={size}")["userProfileList"]

	def change_welcome_message(self, message: str, isEnabled: bool = True):
		"""
		Change welcome message of community.

		**Parameters**
		- message: welcome message
		- isEnabled: Enable welcome message?
		"""
		data = {
			"path": "general.welcomeMessage",
			"value": {
				"enabled": isEnabled,
				"text": message
			}
		}
		return self.req.request("POST", f"/x{self.comId}/s/community/configuration", data)

	def change_community_invite_permission(self, onlyAdmins: bool = True) -> int:
		"""
		permission to invite to the community

		**Parameters**
		- onlyAdmins: only Admins can invite ?
		"""
		data = {
			"path": "general.invitePermission",
			"value": 2 if onlyAdmins is True else 1,
			"action": "set"
		}
		return self.req.request("POST", f"/x{self.comId}/s/community/configuration", data)


	def change_community_aminoId(self, aminoId: str):
		"""
		Change AminoID of community.

		**Parameters**
		- aminoId: amino Id
		"""
		data = {
			"endpoint": aminoId,
		}
		return self.req.request("POST", f"/x{self.comId}/s/community/settings", data)

	def change_guidelines(self, message: str):
		"""
		Change rules of community.

		**Parameters**
		- message: text
		"""
		data = {"content": message}
		return self.req.request("POST", f"/x{self.comId}/s/community/guideline", data)

	def edit_community(self, name: str | None = None, description: str | None = None, aminoId: str | None = None, primaryLanguage: str | None = None, themePackUrl: str | None = None):
		"""
		Edit community.

		**Parameters**
		- name: community name
		- description: community description
		- aminoId: community aminoId
		- primaryLanguage: community language
		- themePackUrl: community theme pack (use ``upload_themepack()``)
		"""
				
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
		"""
		Enable or disable module.

		**Parameters**
		- module: use ``amino.arguments.CommunityModules. some``
		- isEnabled: enable the module?
		"""
		if module not in CommunityModules.all:raise SpecifyType(f"[CommunityModules.all] -> Available community modules: {CommunityModules.all}")
		data = {
			"path": module,
			"value": isEnabled
		}
		return self.req.request("POST", f"/x{self.comId}/s/community/configuration", data)
	
	def add_influencer(self, userId: str, monthlyFee: int):
		"""
		Create user fanclub.

		**Parameters**
		- userId: user Id
		- monthlyFee: subscription cost per month
			- can be maximum 500 coins per month
		"""
		data = {
			"monthlyFee": monthlyFee
		}
		return self.req.request("POST", f"/x{self.comId}/s/influencer/{userId}", data)
		

	def remove_influencer(self, userId: str):
		"""
		Delete user fanclub.

		**Parameters**
		- userId: user id
		"""
		return self.req.request("DELETE", f"/x{self.comId}/s/influencer/{userId}")

	def get_notice_list(self, start: int = 0, size: int = 25):
		"""
		Get notices list.

		**Parameters**
		- start: start pos
		- size: how much you want to get
		"""
		return self.req.request("GET", f"/x{self.comId}/s/notice?type=management&status=1&start={start}&size={size}")["noticeList"]

	def delete_pending_role(self, noticeId: str):
		"""
		Delete pending role.

		**Parameters**
		- noticeId: notice Id
		"""
		return self.req.request("DELETE", f"/x{self.comId}/s/notice/{noticeId}")