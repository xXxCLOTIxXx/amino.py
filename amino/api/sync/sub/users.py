from amino.api.base import BaseClass
from amino import args, WrongType
from uuid import uuid4
from amino import timezone
from amino import BaseObject, UserProfile

class CommunityUsersModule(BaseClass):
	comId: str | int | None

	def get_vip_users(self, comId: str | int | None = None):
		"""
		Get VIP users of community. VIP is basically fanclubs.
		"""

		return self.req.make_sync_request("GET", f"/{self.comId}/s/influencer").json()


	def add_to_favorites(self, userId: str, comId: str | int | None = None) -> BaseObject:
		"""
		Adding user to favotites.

		**Parameters**
		- userId : ID of the User.
		"""
		return BaseObject(self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/user-group/quick-access/{userId}").json())


	def follow(self, userId: str | list, comId: str | int | None = None):
		"""
		Follow an User or Multiple Users.

		**Parameters**
		- userId : ID of the User or List of IDs of the Users.
		"""
		
		if isinstance(userId, str):
			return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/user-profile/{userId}/member").json()
		elif isinstance(userId, list):
			data = { "targetUidList": userId }
			return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/user-profile/{self.userId}/joined", data).json()
		else: raise WrongType(f"userId: {type(userId)}")

	def unfollow(self, userId: str, comId: str | int | None = None):
		"""
		Unfollow an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.make_sync_request("DELETE", f"/x{comId or self.comId}/s/user-profile/{self.userId}/joined/{userId}").json()

	def block(self, userId: str, comId: str | int | None = None):
		"""
		Block an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/block/{userId}").json()

	def unblock(self, userId: str, comId: str | int | None = None):
		"""
		Unblock an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.make_sync_request("DELETE",  f"/x{comId or self.comId}/s/block/{userId}").json()


	def visit(self, userId: str, comId: str | int | None = None):
		"""
		Visit an User

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.make_sync_request("GET",  f"/x{comId or self.comId}/s/user-profile/{userId}?action=visit").json()



	def subscribe_influencer(self, userId: str, autoRenew: bool = False, transactionId: str | None = None, comId: str | int | None = None):
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
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/influencer/{userId}/subscribe", data).json()


	def get_all_users(self, type: str = args.UsersTypes.Recent, start: int = 0, size: int = 25, comId: str | int | None = None) -> list[UserProfile]:
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
		if type not in args.UsersTypes.all:raise WrongType(f"type: {type} not in {args.UsersTypes.all}")
		result = self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/user-profile?type={type}&start={start}&size={size}").json()["userProfileList"]
		return [UserProfile(x) for x in result]

	def get_online_users(self, start: int = 0, size: int = 25, comId: str | int | None = None) -> list[UserProfile]:
		"""
		Get info about all online members.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		result = self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/live-layer?topic=ndtopic:x{self.comId}:online-members&start={start}&size={size}").json()["userProfileList"]
		return [UserProfile(x) for x in result]

	def get_online_favorite_users(self, start: int = 0, size: int = 25, comId: str | int | None = None) -> list[UserProfile]:
		"""
		Get info about all online favorite members.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		result = self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/user-group/quick-access?type=online&start={start}&size={size}").json()["userProfileList"]
		return [UserProfile(x) for x in result]


	def get_user_info(self, userId: str, comId: str | int | None = None) -> UserProfile:
		"""
		Information of an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return UserProfile(self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/user-profile/{userId}").json())

	def get_user_following(self, userId: str, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		List of Users that the User is Following.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/user-profile/{userId}/joined?start={start}&size={size}").json()["userProfileList"]

	def get_user_followers(self, userId: str, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		List of Users that are Following the User.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/user-profile/{userId}/member?start={start}&size={size}").json()["userProfileList"]

	def get_user_checkins(self, userId: str, tz: int | None = None, comId: str | int | None = None):
		"""
		Get info about user's check ins.

		**Parameters**
		- userId: user id
		- tz: time zone
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/check-in/stats/{userId}?timezone={tz if tz else timezone()}").json()


	def get_user_visitors(self, userId: str, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		List of Users that Visited the User.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/user-profile/{userId}/visitors?start={start}&size={size}").json()



	def get_user_achievements(self, userId: str, comId: str | int | None = None):
		"""
		Get info about user's achievements.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/user-profile/{userId}/achievements").json()["achievements"]

	def get_influencer_fans(self, userId: str, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Get all who subscribed to fanclub.

		**Parameters**:
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/influencer/{userId}/fans?start={start}&size={size}").json()



	def get_blocked_users(self, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		List of Users that the User Blocked.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.

		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/block?start={start}&size={size}").json()["userProfileList"]

	def get_blocker_users(self, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		List of Users that are Blocking the User.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/block?start={start}&size={size}").json()["blockerUidList"]

	def search_users(self, nickname: str, start: int = 0, size: int = 25, comId: str | int | None = None) -> list[UserProfile]:
		"""
		Searching users by nickname.

		**Parameters**
		- nickname : user nickname
		- start : Where to start the list.
		- size : Size of the list.
		"""
		result = self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/user-profile?type=name&q={nickname}&start={start}&size={size}").json()["userProfileList"]
		return [UserProfile(x) for x in result]
