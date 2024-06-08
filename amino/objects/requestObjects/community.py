from .user_profile import UserProfile
from .ranking_table_list import RankingTableList
from typing import Optional, Dict

class Community:
	__slots__ = (
		"data", "agent", "rankingTable", "usersCount", "createdTime", "aminoId",
		"icon", "link", "comId", "modifiedTime", "status", "joinType", "tagline",
		"primaryLanguage", "heat", "themePack", "probationStatus", "listedStatus",
		"userAddedTopicList", "name", "isStandaloneAppDeprecated", "searchable",
		"influencerList", "keywords", "mediaList", "description",
		"isStandaloneAppMonetizationEnabled", "advancedSettings", "activeInfo",
		"configuration", "extensions", "nameAliases", "templateId",
		"promotionalMediaList", "defaultRankingTypeInLeaderboard",
		"joinedBaselineCollectionIdList", "newsfeedPages", "catalogEnabled",
		"pollMinFullBarVoteCount", "leaderboardStyle", "facebookAppIdList",
		"welcomeMessage", "welcomeMessageEnabled", "hasPendingReviewRequest",
		"frontPageLayout", "themeColor", "themeHash", "themeVersion", "themeUrl",
		"themeHomePageAppearance", "themeLeftSidePanelTop", "themeLeftSidePanelBottom",
		"themeLeftSidePanelColor", "customList"
	)

	def __init__(self, data: dict):
		if not data:
			for attr in self.__slots__:
				setattr(self, attr, None)

			return

		self.data = data

		self.agent = UserProfile(data.get("agent"))

		themePack: Dict = data.get("themePack", {})
		configuration: Dict = data.get("configuration", {})
		appearance: Dict = configuration.get("appearance", {})
		leftSidePanel: Dict = appearance.get("leftSidePanel", {})
		style: Dict = leftSidePanel.get("style", {})
		page: Dict = configuration.get("page", {})
		advancedSettings: Dict = data.get("advancedSettings", {})
		self.rankingTable = RankingTableList(advancedSettings.get("rankingTable"))
		extensions: Dict = data.get("extensions") or {}

		self.name: Optional[str] = data.get("name")
		self.usersCount: Optional[int] = data.get("membersCount")
		self.createdTime: Optional[str] = data.get("createdTime")
		self.aminoId = data.get("endpoint")
		self.icon = data.get("icon")
		self.link = data.get("link")
		self.comId = data.get("ndcId")
		self.modifiedTime = data.get("modifiedTime")
		self.status = data.get("status")
		self.joinType = data.get("joinType")
		self.primaryLanguage = data.get("primaryLanguage")
		self.heat = data.get("communityHeat")
		self.userAddedTopicList = data.get("userAddedTopicList")
		self.probationStatus = data.get("probationStatus")
		self.listedStatus = data.get("listedStatus")
		self.themePack = themePack
		self.themeColor = themePack.get("themeColor")
		self.themeHash = themePack.get("themePackHash")
		self.themeVersion = themePack.get("themePackRevision")
		self.themeUrl = themePack.get("themePackUrl")
		self.themeHomePageAppearance = appearance.get("homePage")
		self.themeLeftSidePanelTop = leftSidePanel.get("navigation")
		self.themeLeftSidePanelBottom = leftSidePanel.get("navigation")
		self.themeLeftSidePanelColor = style.get("iconColor")
		self.customList = page.get("customList")
		self.tagline = data.get("tagline")
		self.searchable = data.get("searchable")
		self.isStandaloneAppDeprecated = data.get("isStandaloneAppDeprecated")
		self.influencerList = data.get("influencerList")
		self.keywords = data.get("keywords")
		self.mediaList = data.get("mediaList")
		self.description = data.get("content")
		self.isStandaloneAppMonetizationEnabled = data.get("isStandaloneAppMonetizationEnabled")
		self.advancedSettings = advancedSettings
		self.defaultRankingTypeInLeaderboard = advancedSettings.get("defaultRankingTypeInLeaderboard")
		self.frontPageLayout = advancedSettings.get("frontPageLayout")
		self.hasPendingReviewRequest = advancedSettings.get("hasPendingReviewRequest")
		self.welcomeMessageEnabled = advancedSettings.get("welcomeMessageEnabled")
		self.welcomeMessage = advancedSettings.get("welcomeMessageText")
		self.pollMinFullBarVoteCount = advancedSettings.get("pollMinFullBarVoteCount")
		self.catalogEnabled = advancedSettings.get("catalogEnabled")
		self.leaderboardStyle = advancedSettings.get("leaderboardStyle")
		self.facebookAppIdList = advancedSettings.get("facebookAppIdList")
		self.newsfeedPages = advancedSettings.get("newsfeedPages")
		self.joinedBaselineCollectionIdList = advancedSettings.get("joinedBaselineCollectionIdList")
		self.activeInfo = data.get("activeInfo")
		self.configuration = configuration
		self.extensions = extensions
		self.nameAliases = extensions.get("communityNameAliases")
		self.templateId = data.get("templateId")
		self.promotionalMediaList = data.get("promotionalMediaList")