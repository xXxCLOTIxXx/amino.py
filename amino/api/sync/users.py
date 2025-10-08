from amino.api.base import BaseClass
from amino import WrongType, DeprecatedFunction

from amino import UserProfile, BaseObject

class GlobalUsersModule(BaseClass):

	def get_user_info(self, userId: str) -> UserProfile:
		"""
		Information of an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return UserProfile(self.req.make_sync_request("GET", f"/g/s/user-profile/{userId}").json())

	def get_user_following(self, userId: str, start: int = 0, size: int = 25) -> list[UserProfile]:
		"""
		List of Users that the User is Following.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		result = self.req.make_sync_request("GET", f"/g/s/user-profile/{userId}/joined?start={start}&size={size}").json()
		return [UserProfile(x) for x in result["userProfileList"]]

	def get_user_followers(self, userId: str, start: int = 0, size: int = 25) -> list[UserProfile]:
		"""
		List of Users that are Following the User.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		result = self.req.make_sync_request("GET", f"/g/s/user-profile/{userId}/member?start={start}&size={size}").json()
		return [UserProfile(x) for x in result["userProfileList"]]

	def get_user_visitors(self, userId: str, start: int = 0, size: int = 25) -> list[UserProfile]:
		"""
		List of Users that Visited the User.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		result = self.req.make_sync_request("GET", f"/g/s/user-profile/{userId}/visitors?start={start}&size={size}").json()
		return [UserProfile(x) for x in result["visitors"]]


	def visit(self, userId: str) -> UserProfile:
		"""
		Visit an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return UserProfile(self.req.make_sync_request("GET", f"/g/s/user-profile/{userId}?action=visit").json())


	def get_blocked_users(self, start: int = 0, size: int = 25) -> list[UserProfile]:
		"""
		List of Users that the User Blocked.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""

		result = self.req.make_sync_request("GET", f"/g/s/block?start={start}&size={size}").json()["userProfileList"]
		return  [UserProfile(x) for x in result]

	def get_blocker_users(self, start: int = 0, size: int = 25) -> list[str]:
		"""
		Get a list of users who have blocked you

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/g/s/block/full-list?start={start}&size={size}").json()["blockerUidList"]

	def follow(self, userId: str) -> BaseObject:
		#TODO FIX
		"""
		Follow an User

		**Parameters**
		- userId : ID of the User
		"""
		raise DeprecatedFunction
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/user-profile/{userId}/member").json())

	def unfollow(self, userId: str) -> BaseObject:
		"""
		Unfollow an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return BaseObject(self.req.make_sync_request("DELETE", f"/g/s/user-profile/{userId}/member/{self.userId}").json())

	def block(self, userId: str) -> BaseObject:
		#TODO FIX
		"""
		Block an User.

		**Parameters**
		- userId : ID of the User.
		"""
		raise DeprecatedFunction
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/block/{userId}").json())
	
	def unblock(self, userId: str) -> BaseObject:
		"""
		Unblock an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return BaseObject(self.req.make_sync_request("DELETE", f"/g/s/block/{userId}").json())

	def get_all_users(self, start: int = 0, size: int = 25) -> list[UserProfile]:
		"""
		Get list of users of Amino.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return [UserProfile(x) for x in self.req.make_sync_request("GET", f"/g/s/user-profile?type=recent&start={start}&size={size}").json()["userProfileList"]]
	
