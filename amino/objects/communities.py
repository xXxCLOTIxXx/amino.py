from .base_object import BaseObject
from . import UserProfile


class RankingTableList:
    def __init__(self, data: dict):
        self.data = data
        self.title = data.get("title")
        self.level = data.get("level")
        self.reputation = data.get("reputation")
        self.id = data.get("id")



class Community(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)
        data = data or {}
        if data.get("refObject") is not None:data= data.get("refObject", {})
        if data.get("community") is not None:data = data.get("community", {})
        
        self.agent: UserProfile = UserProfile(data.get("agent", {}))
        self.rankingTable: list[RankingTableList] = [RankingTableList(x) for x in data.get("advancedSettings", {}).get("rankingTable", [])]

        self.usersCount = data.get("membersCount")
        self.createdTime = data.get("createdTime")
        self.aminoId = data.get("endpoint")
        self.icon = data.get("icon")
        self.link = data.get("link")
        self.comId = data.get("ndcId")
        self.modifiedTime = data.get("modifiedTime")
        self.status = data.get("status")
        self.joinType = data.get("joinType")
        self.tagline = data.get("tagline")
        self.primaryLanguage = data.get("primaryLanguage")
        self.heat = data.get("communityHeat")
        self.themePack: dict = data.get("themePack", {})
        self.probationStatus = data.get("probationStatus")
        self.listedStatus = data.get("listedStatus")
        self.userAddedTopicList = data.get("userAddedTopicList")
        self.name = data.get("name")
        self.isStandaloneAppDeprecated = data.get("isStandaloneAppDeprecated")
        self.searchable = data.get("searchable")
        self.influencerList = data.get("influencerList")
        self.keywords = data.get("keywords")
        self.mediaList = data.get("mediaList")
        self.description = data.get("description")
        self.isStandaloneAppMonetizationEnabled = data.get("isStandaloneAppMonetizationEnabled")
        self.advancedSettings: dict = data.get("advancedSettings", {})
        self.activeInfo = data.get("activeInfo")
        self.configuration: dict = data.get("configuration", {})
        self.extensions: dict = data.get("extensions", {})
        self.nameAliases = self.extensions.get("communityNameAliases") if self.extensions else None
        self.templateId = data.get("templateId")
        self.promotionalMediaList = data.get("promotionalMediaList")
        self.defaultRankingTypeInLeaderboard = self.advancedSettings.get("defaultRankingTypeInLeaderboard")
        self.joinedBaselineCollectionIdList = self.advancedSettings.get("joinedBaselineCollectionIdList")
        self.newsfeedPages = self.advancedSettings.get("newsfeedPages")
        self.catalogEnabled = self.advancedSettings.get("catalogEnabled")
        self.pollMinFullBarVoteCount = self.advancedSettings.get("pollMinFullBarVoteCount")
        self.leaderboardStyle = self.advancedSettings.get("leaderboardStyle")
        self.facebookAppIdList = self.advancedSettings.get("facebookAppIdList")
        self.welcomeMessage = self.advancedSettings.get("welcomeMessageText")
        self.welcomeMessageEnabled = self.advancedSettings.get("welcomeMessageEnabled")
        self.hasPendingReviewRequest = self.advancedSettings.get("hasPendingReviewRequest")
        self.frontPageLayout = self.advancedSettings.get("frontPageLayout")
        self.themeColor = self.themePack.get("themeColor")
        self.themeHash = self.themePack.get("themePackHash")
        self.themeVersion = self.themePack.get("themePackRevision")
        self.themeUrl = self.themePack.get("themePackUrl")
        self.themeHomePageAppearance = self.configuration.get("appearance", {}).get("homePage", {}).get("navigation")
        self.themeLeftSidePanelTop = self.configuration.get("appearance", {}).get("leftSidePanel", {}).get("navigation", {}).get("level1")
        self.themeLeftSidePanelBottom = self.configuration.get("appearance", {}).get("leftSidePanel", {}).get("navigation", {}).get("level2")
        self.themeLeftSidePanelColor = self.configuration.get("appearance", {}).get("leftSidePanel", {}).get("style", {}).get("iconColor")
        self.customList = self.configuration.get("page", {}).get("customList")