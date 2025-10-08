from amino.api.base import BaseClass
from amino import SpecifyType, WrongType, args
from amino.helpers.generator import timezone

from uuid import uuid4

class CommunityOtherModule(BaseClass):
	comId: str | int | None

	def check_in(self, tz: int | None = None, comId: str | int | None = None):
		"""
		Check in community.

		**Parameters**:
		- tz: time zone
			- better dont touch
		"""
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/check-in", { "timezone": tz if tz else timezone()}).json()



	def get_invite_codes(self, status: str = "normal", start: int = 0, size: int = 25, comId: str | int | None = None):
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
		return self.req.make_sync_request("GET", f"/g/s-x{comId or self.comId}/community/invitation?status={status}&start={start}&size={size}").json()["communityInvitationList"]

	def generate_invite_code(self, duration: int = 0, force: bool = True, comId: str | int | None = None):
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
		return self.req.make_sync_request("POST", f"/g/s-x{comId or self.comId}/community/invitation", data).json()["communityInvitation"]

	def delete_invite_code(self, inviteId: str, comId: str | int | None = None):
		"""
		Delete invite code from community. If you have rights, of course.

		**Parameters**:
		- inviteId: str
			- its NOT invite code
			- yes, you can get it. using function `get_invite_codes`
		"""
		return self.req.make_sync_request("DELETE", f"/g/s-x{comId or self.comId}/community/invitation/{inviteId}").json()


	def repair_check_in(self, repair_method: str = args.RepairMethod.Coins, comId: str | int | None = None):
		"""
		Repairing check in streak.

		**Parameters**
		- method: int = RepairMethod.Coins
			- if ``amino.arguments.RepairMethod.Coins``, it will use coins
			- if ``amino.arguments.RepairMethod.AminoPlus``, it will use Amino+ superpower
		"""
		if repair_method not in args.RepairMethod.all: raise WrongType(repair_method)
		data = {
			"repairMethod": repair_method
		}

		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/check-in/repair", data)


	def lottery(self, tz: int | None = None, comId: str | int | None = None):
		"""
		Testing your luck in lottery. Once a day, of course.

		**Parameters**
		- tz: int 
			- better dont touch
		"""
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/check-in/lottery", { "timezone": tz if tz else timezone()}).json()["lotteryLog"]


	def send_active_obj(self, startTime: int | None = None, endTime: int | None = None, tz: int | None = None, timers: list | None = None, comId: str | int | None = None):
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

		return self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/community/stats/user-active-time", data).json()


	def send_coins(self, coins: int, blogId: str | None = None, chatId: str | None = None, objectId: str | None = None, transactionId: str | None = None, comId: str | int | None = None):
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

		if blogId is not None: url = f"/x{comId or self.comId}/s/blog/{blogId}/tipping"
		elif chatId is not None: url = f"/x{comId or self.comId}/s/chat/thread/{chatId}/tipping"
		elif objectId is not None:
			data["objectId"] = objectId
			data["objectType"] = 2
			url = f"/x{comId or self.comId}/s/tipping"
		else: raise SpecifyType

		return self.req.make_sync_request("POST", url, data).json()

	def thank_tip(self, chatId: str, userId: str, comId: str | int | None = None):
		"""
		Thank you for the coins

		**Parameters**
		- chatId : ID of the Blog.
		- userId : ID of the Chat.
		"""
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}/tipping/tipped-users/{userId}/thank").json()


	def flag(self, reason: str, flagType: int, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None, asGuest: bool = False, comId: str | int | None = None):
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

		return self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/{'g-flag' if asGuest else 'flag'}", data).json()



	def get_leaderboard_info(self, type: int = args.LeaderboardTypes.Day, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Recieve all your users from leaderboard.

		**Parameters**
		- type: leaderboard type (use ``amino.arguments.LeaderboardTypes``)
		- start : Where to start the list.
		- size : Size of the list.
		"""
		if type not in args.LeaderboardTypes.all:raise WrongType(f"LeaderboardTypes.all: {type} not in {args.LeaderboardTypes.all}")
		url = f"/g/s-x{comId or self.comId}/community/leaderboard?rankingType={type}&start={start}"
		if type != 4:url += f"&size={size}"

		return self.req.make_sync_request("GET", url).json()["userProfileList"]


	def get_store_chat_bubbles(self, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Getting all available chat bubbles from store.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/store/items?sectionGroupId=chat-bubble&start={start}&size={size}").json()
	

	def get_live_layer(self, comId: str | int | None = None):
		"""
		Get live layer.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/live-layer/homepage?v=2").json()["liveLayerList"]


	def apply_bubble(self, bubbleId: str, chatId: str, applyToAll: bool = False, comId: str | int | None = None):

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

		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/chat/thread/apply-bubble", data).json()


	def apply_avatar_frame(self, avatarId: str, applyToAll: bool = True, comId: str | int | None = None):
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
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/avatar-frame/apply", data).json()


	def purchase(self, objectId: str, objectType: int = args.PurchaseTypes.Bubble, aminoPlus: bool = True, autoRenew: bool = False, comId: str | int | None = None):
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

		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/store/purchase", data).json()
