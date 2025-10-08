from amino.api.base import BaseClass
from amino import Community, UserProfile, BaseObject, DeprecatedFunction


class GlobalCommunitiesModule(BaseClass):
	

	def my_communities(self, start: int = 0, size: int = 25) -> list[Community]:
		"""
		List of Communities the account is in.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		result = self.req.make_sync_request("GET", f"/g/s/community/joined?v=1&start={start}&size={size}").json()
		return [Community({"community": x}) for x in result.get("communityList", [])]

	def profiles_in_communities(self, start: int = 0, size: int = 25) -> list[UserProfile]:
		"""
		Getting your profiles in communities.

		**Parameters**:
		- start : Where to start the list.
		- size : Size of the list.
		"""
		result =  self.req.make_sync_request("GET", f"/g/s/community/joined?v=1&start={start}&size={size}").json()
		return [UserProfile(x) for x in result.get("userInfoInCommunities", {}).values()]
	
	def get_community_info(self, comId: int) -> Community:
		"""
		Information of an Community.

		**Parameters**
		- comId : ID of the Community.
		"""
		return Community(self.req.make_sync_request("GET", f"/g/s-x{comId}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount").json())

	def search_community(self, aminoId: str) -> list[Community]:
		"""
		Search a Community by Amino ID.

		**Parameters**
		- aminoId : Amino ID of the Community.
		"""
		result = self.req.make_sync_request("GET", f"/g/s/search/amino-id-and-link?q={aminoId}").json()
		return [Community(x) for x in result.get("resultList", [])]

	def join_community(self, comId: int, invitationId: str | None = None) -> BaseObject:
		"""
		Join a Community.

		**Parameters**
		- comId : ID of the Community.
		- invitationId : ID of the Invitation Code.
		"""
		raise DeprecatedFunction
		
		data = {}
		if invitationId:data["invitationId"] = invitationId
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId}/s/community/join", data).json())

	def request_join_community(self, comId: int, message: str | None = None) -> BaseObject:
		"""
		Request to join a Community.

		**Parameters**
		- comId : ID of the Community.
		- message : Message to be sent.
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId}/s/community/membership-request", {"message": message}).json())

	def leave_community(self, comId: int) -> BaseObject:
		"""
		Leave a Community.

		**Parameters**
		- comId : ID of the Community.
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId}/s/community/leave").json())

	def flag_community(self, comId: int, reason: str, flagType: int, isGuest: bool = False) -> BaseObject:
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
		return BaseObject(self.req.make_sync_request("POST", f"/x{comId}/s/{'g-flag' if isGuest else 'flag'}", data).json())

	def get_linked_communities(self, userId: str) -> list[Community]:
		"""
		Get a List of Linked Communities of an User.

		**Parameters**
		- userId : ID of the User.
		"""
		result = self.req.make_sync_request("GET", f"/g/s/user-profile/{userId}/linked-community").json()["linkedCommunityList"]
		return [Community(x) for x in result]

	def get_unlinked_communities(self, userId: str) -> list[Community]:
		"""
		Get a List of Unlinked Communities of an User.

		**Parameters**
		- userId : ID of the User.
		"""
		result = self.req.make_sync_request("GET", f"/g/s/user-profile/{userId}/linked-community").json()["unlinkedCommunityList"]
		return [Community(x) for x in result]

	def reorder_linked_communities(self, comIds: list) -> BaseObject:
		"""
		Reorder List of Linked Communities.

		**Parameters**
		- comIds : IDS of the Communities.
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/user-profile/{self.userId}/linked-community/reorder", {"ndcIds": comIds}).json())

	def add_linked_community(self, comId: int) -> BaseObject:
		"""
		Add a Linked Community on your profile.

		**Parameters**
			- comId : ID of the Community.
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/user-profile/{self.userId}/linked-community/{comId}").json())

	def remove_linked_community(self, comId: int) -> BaseObject:
		"""
		Remove a Linked Community on your profile.

		**Parameters**
		- comId : ID of the Community.
		"""
		return BaseObject(self.req.make_sync_request("DELETE", f"/g/s/user-profile/{self.userId}/linked-community/{comId}").json())

	def get_public_communities(self, language: str = "en", size: int = 25) -> list[Community]:
		"""
		Get public communites

		**Parameters**
		- language : Set up language
		- size : Size of the list.
		"""
		result =self.req.make_sync_request("GET", f"/g/s/topic/0/feed/community?language={language}&type=web-explore&categoryKey=recommendation&size={size}&pagingType=t").json()
		return [Community(x) for x in result.get("communityList", [])]
