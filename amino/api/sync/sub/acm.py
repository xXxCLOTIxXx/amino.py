from amino.api.base import BaseClass
from amino import args, WrongType, SpecifyType, MediaObject
from typing import BinaryIO

class ACMModule(BaseClass):
	comId: str | int | None
	def upload_media(self, file: BinaryIO, fileType: str | None = None) -> MediaObject: ...


	def create_community(self, name: str, tagline: str, icon: BinaryIO, themeColor: str, joinType: int = args.CommunityJoinTypes.Open, primaryLanguage: str = "en"):
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
				"path": self.upload_media(icon).mediaValue,
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

		return self.req.make_sync_request("POST", f"/g/s/community", data).json()


	def get_community_themepack_info(self, comId: str | int | None = None):
		"""
		This method can be used for getting info about current themepack of community.
		"""
		return self.req.make_sync_request("POST", f"/g/s-x{comId or self.comId}/community/info?withTopicList=1&withInfluencerList=1&influencerListOrderStrategy=fansCount").json()['community']['themePack']

	def upload_themepack(self, file: BinaryIO, comId: str | int | None = None):
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
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/media/upload/target/community-theme-pack", file.read()).json()

	def delete_community(self, email: str, password: str, verificationCode: str, comId: str | int | None = None):
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
		return self.req.make_sync_request("POST", f"/g/s-x{comId or self.comId}/community/delete-request", data).json()

	def my_managed_communities(self, start: int = 0, size: int = 25):
		"""
		Getting all communities where you are leader.

		**Parameters**
		- start: start pos
		- size: how much you want to get
		"""
		return self.req.make_sync_request("GET", f"/g/s/community/managed?start={start}&size={size}").json()["communityList"]

	def get_categories(self, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Getting categories of communities.

		**Parameters**
		- start: start pos
		- size: how much you want to get
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/blog-category?start={start}&size={size}").json()

	def change_sidepanel_color(self, color: str, comId: str | int | None = None):
		"""
		Change sidepanel color.

		**Parameters**
		- color: should be hex color like "#123ABC"
		"""
		data = {
			"path": "appearance.leftSidePanel.style.iconColor",
			"value": color
		}
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/community/configuration", data).json()

	def promote(self, userId: str, rank: str, comId: str | int | None = None):
		"""
		Promote user to curator, leader or agent.

		**Parameters**
		- userId: user Id
		- rank: can be only "agent"/"transfer-agent", "leader" or "curator"
			- use ``amino.arguments.AdministratorsRank. some``
		"""
		if rank not in args.AdministratorsRank.all:raise SpecifyType(f"[AdministratorsRank.all] -> Available ranks: {args.AdministratorsRank.all}")
		rank = rank.lower().replace("agent", "transfer-agent")
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/user-profile/{userId}/{rank}").json()

	def get_join_requests(self, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Get all requests to join your community.

		**Parameters**
		- start: start pos
		- size: how much you want to get
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/community/membership-request?status=pending&start={start}&size={size}").json()
	
	def accept_join_request(self, userId: str, comId: str | int | None = None):
		"""
		Accept user to join your community.

		**Parameters**
		- user Id: str
		"""
		data = {}
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/community/membership-request/{userId}/accept", data).json()
	
	def reject_join_request(self, userId: str, comId: str | int | None = None):
		"""
		Reject user to join your community.

		**Parameters**
		- userId: user id
		"""
		data = {}
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/community/membership-request/{userId}/reject", data).json()

	def get_community_stats(self, comId: str | int | None = None):
		"""
		Get community statistics.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/community/stats").json()["communityStats"]

	def get_community_moderation_stats(self, type: str = "leader", start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Get community moderation statistics.

		**Parameters**
		- type: can be only "leader" or "curator"
		- start: start pos
		- size: how much you want to get
		"""
		if type.lower() not in ("leader", "curator"):raise WrongType(f"{type} not in ('leader', 'curator')")
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/community/stats/moderation?type={type.lower()}&start={start}&size={size}").json()["userProfileList"]

	def change_welcome_message(self, message: str, isEnabled: bool = True, comId: str | int | None = None):
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
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/community/configuration", data).json()

	def change_community_invite_permission(self, onlyAdmins: bool = True, comId: str | int | None = None):
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
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/community/configuration", data).json()


	def change_community_aminoId(self, aminoId: str, comId: str | int | None = None):
		"""
		Change AminoID of community.

		**Parameters**
		- aminoId: amino Id
		"""
		data = {
			"endpoint": aminoId,
		}
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/community/settings", data).json()

	def change_guidelines(self, message: str, comId: str | int | None = None):
		"""
		Change rules of community.

		**Parameters**
		- message: text
		"""
		data = {"content": message}
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/community/guideline", data).json()

	def edit_community(self, name: str | None = None, description: str | None = None, aminoId: str | None = None, primaryLanguage: str | None = None, themePackUrl: str | None = None, comId: str | int | None = None):
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
		
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/community/settings", data).json()

	def change_module(self, module: str, isEnabled: bool, comId: str | int | None = None):
		"""
		Enable or disable module.

		**Parameters**
		- module: use ``amino.arguments.CommunityModules. some``
		- isEnabled: enable the module?
		"""
		if module not in args.CommunityModules.all:raise SpecifyType(f"[CommunityModules.all] -> Available community modules: {args.CommunityModules.all}")
		data = {
			"path": module,
			"value": isEnabled
		}
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/community/configuration", data).json()
	
	def add_influencer(self, userId: str, monthlyFee: int, comId: str | int | None = None):
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
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/influencer/{userId}", data).json()
		

	def remove_influencer(self, userId: str, comId: str | int | None = None):
		"""
		Delete user fanclub.

		**Parameters**
		- userId: user id
		"""
		return self.req.make_sync_request("DELETE", f"/x{comId or self.comId}/s/influencer/{userId}").json()

	def get_notice_list(self, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Get notices list.

		**Parameters**
		- start: start pos
		- size: how much you want to get
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/notice?type=management&status=1&start={start}&size={size}").json()["noticeList"]

	def delete_pending_role(self, noticeId: str, comId: str | int | None = None):
		"""
		Delete pending role.

		**Parameters**
		- noticeId: notice Id
		"""
		return self.req.make_sync_request("DELETE", f"/x{comId or self.comId}/s/notice/{noticeId}").json()