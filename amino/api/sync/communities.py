from amino.api.base import BaseClass

class GlobalCommunitiesModule(BaseClass):
	

	def my_communities(self, start: int = 0, size: int = 25):
		"""
		List of Communities the account is in.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/g/s/community/joined?v=1&start={start}&size={size}").json()["communityList"]

	def profiles_in_communities(self, start: int = 0, size: int = 25):
		"""
		Getting your profiles in communities.

		**Parameters**:
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/g/s/community/joined?v=1&start={start}&size={size}").json()["userInfoInCommunities"]
	
	def get_community_info(self, comId: int):
		"""
		Information of an Community.

		**Parameters**
		- comId : ID of the Community.
		"""
		return self.req.make_sync_request("GET", f"/g/s-x{comId}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount").json()["community"]

	def search_community(self, aminoId: str):
		"""
		Search a Community by Amino ID.

		**Parameters**
		- aminoId : Amino ID of the Community.
		"""
		return self.req.make_sync_request("GET", f"/g/s/search/amino-id-and-link?q={aminoId}").json()["resultList"]

	def join_community(self, comId: int, invitationId: str | None = None):
		"""
		Join a Community.

		**Parameters**
		- comId : ID of the Community.
		- invitationId : ID of the Invitation Code.
		"""
		
		data = {}
		if invitationId:data["invitationId"] = invitationId
		return self.req.make_sync_request("POST", f"/x{comId}/s/community/join", data).json()

	def request_join_community(self, comId: int, message: str | None = None):
		"""
		Request to join a Community.

		**Parameters**
		- comId : ID of the Community.
		- message : Message to be sent.
		"""
		return self.req.make_sync_request("POST", f"/x{comId}/s/community/membership-request", {"message": message}).json()

	def leave_community(self, comId: int):
		"""
		Leave a Community.

		**Parameters**
		- comId : ID of the Community.
		"""
		return self.req.make_sync_request("POST", f"/x{comId}/s/community/leave").json()

	def flag_community(self, comId: int, reason: str, flagType: int, isGuest: bool = False):
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
		return self.req.make_sync_request("POST", f"/x{comId}/s/{'g-flag' if isGuest else 'flag'}", data).json()

	def get_linked_communities(self, userId: str):
		"""
		Get a List of Linked Communities of an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.make_sync_request("GET", f"/g/s/user-profile/{userId}/linked-community").json()["linkedCommunityList"]

	def get_unlinked_communities(self, userId: str):
		"""
		Get a List of Unlinked Communities of an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return self.req.make_sync_request("GET", f"/g/s/user-profile/{userId}/linked-community").json()["unlinkedCommunityList"]

	def reorder_linked_communities(self, comIds: list):
		"""
		Reorder List of Linked Communities.

		**Parameters**
		- comIds : IDS of the Communities.
		"""
		return self.req.make_sync_request("POST", f"/g/s/user-profile/{self.userId}/linked-community/reorder", {"ndcIds": comIds}).json()

	def add_linked_community(self, comId: int):
		"""
		Add a Linked Community on your profile.

		**Parameters**
			- comId : ID of the Community.
		"""
		return self.req.make_sync_request("POST", f"/g/s/user-profile/{self.userId}/linked-community/{comId}").json()

	def remove_linked_community(self, comId: int):
		"""
		Remove a Linked Community on your profile.

		**Parameters**
		- comId : ID of the Community.
		"""
		return self.req.make_sync_request("DELETE", f"/g/s/user-profile/{self.userId}/linked-community/{comId}").json()

	def get_public_communities(self, language: str = "en", size: int = 25):
		"""
		Get public communites

		**Parameters**
		- language : Set up language
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/g/s/topic/0/feed/community?language={language}&type=web-explore&categoryKey=recommendation&size={size}&pagingType=t").json()["communityList"]
