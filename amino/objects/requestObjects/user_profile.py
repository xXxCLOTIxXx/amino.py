from typing import Optional, Dict, List
from .obj_helper import set_attributes



class UserProfile:
	__slots__ = (
		"data", "fanClub", "accountMembershipStatus", "activation", "activePublicLiveThreadId",
		"age", "aminoId", "aminoIdEditable", "avatarFrame", "avatarFrameId",
		"blogsCount", "commentsCount", "content", "createdTime",
		"followersCount", "followingCount", "followingStatus", "gender",
		"icon", "isGlobal", "isNicknameVerified", "itemsCount", "level",
		"mediaList", "membershipStatus", "modifiedTime", "mood", "moodSticker", "nickname",
		"notificationSubscriptionStatus", "onlineStatus", "onlineStatus2",
		"postsCount", "pushEnabled", "race", "reputation", "role", "securityLevel",
		"status", "storiesCount", "tagList", "userId", "verified",
		"totalQuizHighestScore", "totalQuizPlayedTimes", "requestId", "message", "applicant",
		"avgDailySpendTimeIn7Days", "adminLogCountIn7Days", "extensions", "style",
		"backgroundImage", "backgroundColor", "coverAnimation", "customTitles", "defaultBubbleId",
		"disabledLevel", "disabledStatus", "disabledTime", "isMemberOfTeamAmino",
		"privilegeOfChatInviteRequest", "privilegeOfCommentOnUserProfile", "influencerInfo",
		"fansCount", "influencerCreatedTime", "influencerMonthlyFee", "influencerPinned",
		"staffInfo", "globalStrikeCount", "lastStrikeTime", "lastWarningTime", "strikeCount",
		"warningCount", "session"
	)

	def __init__(self, data: Dict):
		if not data:
			for attr in self.__slots__:
				setattr(self, attr, None)

			return

		self.data: Optional[Dict] = data

		self.fanClub = FanClubList(data.get("fanClubList", []))

		self.accountMembershipStatus: Optional[int] = data.get("accountMembershipStatus")
		self.activation: Optional[int] = data.get("activation")
		self.activePublicLiveThreadId: Optional[str] = data.get("activePublicLiveThreadId")
		self.age: Optional[int] = data.get("age")
		self.aminoId: Optional[str] = data.get("aminoId")
		self.aminoIdEditable: Optional[bool] = data.get("aminoIdEditable")
		self.avatarFrame: Optional[str] = data.get("avatarFrame")
		self.avatarFrameId: Optional[str] = data.get("avatarFrameId")
		self.blogsCount: Optional[int] = data.get("blogsCount")
		self.commentsCount: Optional[int] = data.get("commentsCount")
		self.content: Optional[str] = data.get("content")
		self.createdTime: Optional[int] = data.get("createdTime")
		self.followersCount: Optional[int] = data.get("followersCount")
		self.followingCount: Optional[int] = data.get("followingCount")
		self.followingStatus: Optional[int] = data.get("followingStatus")
		self.gender: Optional[str] = data.get("gender")
		self.icon: Optional[str] = data.get("icon")
		self.isGlobal: Optional[bool] = data.get("isGlobal")
		self.isNicknameVerified: Optional[bool] = data.get("isNicknameVerified")
		self.itemsCount: Optional[int] = data.get("itemsCount")
		self.level: Optional[int] = data.get("level")
		self.mediaList = data.get("mediaList")
		self.membershipStatus: Optional[int] = data.get("membershipStatus")
		self.modifiedTime: Optional[int] = data.get("modifiedTime")
		self.mood: Optional[str] = data.get("mood")
		self.moodSticker: Optional[str] = data.get("moodSticker")
		self.nickname: Optional[str] = data.get("nickname")
		self.notificationSubscriptionStatus: Optional[int] = data.get("notificationSubscriptionStatus")
		self.onlineStatus: Optional[int] = data.get("onlineStatus")
		self.onlineStatus2: Optional[int] = data.get("onlineStatus2")
		self.postsCount: Optional[int] = data.get("postsCount")
		self.pushEnabled: Optional[bool] = data.get("pushEnabled")
		self.race: Optional[str] = data.get("race")
		self.reputation: Optional[int] = data.get("reputation")
		self.role: Optional[str] = data.get("role")
		self.securityLevel: Optional[int] = data.get("securityLevel")
		self.status: Optional[str] = data.get("status")
		self.storiesCount: Optional[int] = data.get("storiesCount")
		self.tagList: Optional[List[str]] = data.get("tagList")
		self.userId: Optional[str] = data.get("uid")
		self.verified: Optional[bool] = data.get("verified")
		self.totalQuizHighestScore: Optional[int] = data.get("totalQuizHighestScore")
		self.totalQuizPlayedTimes: Optional[int] = data.get("totalQuizPlayedTimes")
		self.requestId: Optional[str] = data.get("requestId")
		self.message: Optional[str] = data.get("message")
		self.applicant: Optional[str] = data.get("applicant")
		self.avgDailySpendTimeIn7Days: Optional[int] = data.get("avgDailySpendTimeIn7Days")
		self.adminLogCountIn7Days: Optional[int] = data.get("adminLogCountIn7Days")

		# extensions
		self.extensions: Optional[Dict] = data.get("extensions") or {}
		# style
		self.style: Optional[Dict] = self.extensions.get("style") or {}
		self.backgroundImage: Optional[str] = self.style.get("backgroundImage")
		self.backgroundColor: Optional[str] = self.style.get("backgroundColor")

		self.coverAnimation: Optional[str] = self.extensions.get("coverAnimation")
		self.customTitles: Optional[List[str]] = self.extensions.get("customTitles")
		self.defaultBubbleId: Optional[str] = self.extensions.get("defaultBubbleId")
		self.disabledLevel: Optional[int] = self.extensions.get("__disabledLevel__")
		self.disabledStatus: Optional[str] = self.extensions.get("__disabledStatus__")
		self.disabledTime: Optional[int] = self.extensions.get("__disabledTime__")
		self.isMemberOfTeamAmino: Optional[bool] = self.extensions.get("isMemberOfTeamAmino")
		self.privilegeOfChatInviteRequest: Optional[bool] = self.extensions.get("privilegeOfChatInviteRequest")
		self.privilegeOfCommentOnUserProfile: Optional[bool] = self.extensions.get("privilegeOfCommentOnUserProfile")

		# influencerInfo
		self.influencerInfo: Optional[Dict] = data.get("influencerInfo") or {}
		self.fansCount: Optional[int] = self.influencerInfo.get("fansCount")
		self.influencerCreatedTime: Optional[int] = self.influencerInfo.get("createdTime")
		self.influencerMonthlyFee: Optional[int] = data.get("monthlyFee")
		self.influencerPinned: Optional[bool] = data.get("pinned")

		# adminInfo
		self.staffInfo: Optional[Dict] = data.get("adminInfo") or {}
		self.globalStrikeCount: Optional[int] = self.staffInfo.get("globalStrikeCount")
		self.lastStrikeTime: Optional[int] = self.staffInfo.get("lastStrikeTime")
		self.lastWarningTime: Optional[int] = self.staffInfo.get("lastWarningTime")
		self.strikeCount: Optional[int] = self.staffInfo.get("strikeCount")
		self.warningCount: Optional[int] = self.staffInfo.get("warningCount")
		


class UserProfileList:
	__slots__ = (
		"data", "fanClub", "accountMembershipStatus", "activation", "activePublicLiveThreadId",
		"age", "aminoId", "aminoIdEditable", "avatarFrame", "avatarFrameId",
		"blogsCount", "commentsCount", "content", "createdTime",
		"followersCount", "followingCount", "followingStatus", "gender",
		"icon", "isGlobal", "isNicknameVerified", "itemsCount", "level",
		"mediaList", "membershipStatus", "modifiedTime", "mood", "moodSticker", "nickname",
		"notificationSubscriptionStatus", "onlineStatus", "onlineStatus2",
		"postsCount", "pushEnabled", "race", "reputation", "role", "securityLevel",
		"status", "storiesCount", "tagList", "userId", "verified",
		"totalQuizHighestScore", "totalQuizPlayedTimes", "requestId", "message", "applicant",
		"avgDailySpendTimeIn7Days", "adminLogCountIn7Days", "extensions", "style",
		"backgroundImage", "backgroundColor", "coverAnimation", "customTitles", "defaultBubbleId",
		"disabledLevel", "disabledStatus", "disabledTime", "isMemberOfTeamAmino",
		"privilegeOfChatInviteRequest", "privilegeOfCommentOnUserProfile", "influencerInfo",
		"fansCount", "influencerCreatedTime", "influencerMonthlyFee", "influencerPinned",
		"staffInfo", "globalStrikeCount", "lastStrikeTime", "lastWarningTime", "strikeCount",
		"warningCount", "session"
	)

	def __init__(self, data):
		self.data = data
		_userObjects = tuple(UserProfile(x).UserProfile for x in data)

		set_attributes(self, _userObjects)



class FanClubList:
	__slots__ = (
		"data", "profile", "targetUserProfile", "userId", "lastThankedTime",
		"expiredTime", "createdTime", "status", "targetUserId"
	)

	def __init__(self, data):
		if not data:
			for attr in self.__slots__:
				setattr(self, attr, None)

			return

		self.data = data

		profile_data = []
		targetUserProfile_data = []
		userId_data = []
		lastThankedTime_data = []
		expiredTime_data = []
		createdTime_data = []
		status_data = []
		targetUserId_data = []

		for x in data:
			profile_data.append(x.get("fansUserProfile"))
			targetUserProfile_data.append(x.get("targetUserProfile"))
			userId_data.append(x.get("uid"))
			lastThankedTime_data.append(x.get("lastThankedTime"))
			expiredTime_data.append(x.get("expiredTime"))
			createdTime_data.append(x.get("createdTime"))
			status_data.append(x.get("fansStatus"))
			targetUserId_data.append(x.get("targetUid"))

		self.profile = UserProfileList(profile_data)
		self.targetUserProfile = UserProfileList(targetUserProfile_data)
		self.userId = userId_data
		self.lastThankedTime = lastThankedTime_data
		self.expiredTime = expiredTime_data
		self.createdTime = createdTime_data
		self.status = status_data
		self.targetUserId = targetUserId_data
