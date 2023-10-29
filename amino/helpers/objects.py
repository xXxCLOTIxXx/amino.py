
class profile:
	def __init__(self, data: dict = {}):
		self.json = data
		self.sid = self.json.get("sid")
		self.userId = self.json.get("auid")
		self.secret = self.json.get("secret")
		self.account = Account(self.json.get("account", {}))
		self.userProfile = UserProfile(self.json.get("userProfile", {}))


class Account:
	def __init__(self, data: dict = {}):
		self.json = data
		self.username = self.json.get("username")
		self.status = self.json.get("status")
		self.userId = self.json.get("uid")
		self.modifiedTime = self.json.get("modifiedTime")
		self.twitterID = self.json.get("twitterID")
		self.activation = self.json.get("activation")
		self.phoneNumberActivation = self.json.get("phoneNumberActivation")
		self.emailActivation = self.json.get("emailActivation")
		self.appleID = self.json.get("appleID")
		self.nickname = self.json.get("nickname")
		self.mediaList = self.json.get("mediaList")
		self.googleID = self.json.get("googleID")
		self.icon = self.json.get("icon")
		self.securityLevel = self.json.get("securityLevel")
		self.phoneNumber = self.json.get("phoneNumber")
		self.membership = self.json.get("membership")
		self.advancedSettings = self.json.get("advancedSettings")
		self.role = self.json.get("role")
		self.aminoIdEditable = self.json.get("aminoIdEditable")
		self.aminoId = self.json.get("aminoId")
		self.createdTime = self.json.get("createdTime")
		self.extensions = self.json.get("extensions")
		self.email = self.json.get("email")

class UserProfile:
	def __init__(self, data: dict = {}):
		self.json = data
		self.status = self.json.get("status")
		self.moodSticker = self.json.get("moodSticker")
		self.itemsCount = self.json.get("itemsCount")
		self.consecutiveCheckInDays = self.json.get("consecutiveCheckInDays")
		self.userId = self.json.get("uid")
		self.modifiedTime = self.json.get("modifiedTime")
		self.followingStatus = self.json.get("followingStatus")
		self.onlineStatus = self.json.get("onlineStatus")
		self.accountMembershipStatus = self.json.get("accountMembershipStatus")
		self.isGlobal = self.json.get("isGlobal")
		self.reputation = self.json.get("reputation")
		self.postsCount = self.json.get("postsCount")
		self.membersCount = self.json.get("membersCount")
		self.nickname = self.json.get("nickname")
		self.mediaList = self.json.get("mediaList")
		self.icon = self.json.get("icon")
		self.isNicknameVerified = self.json.get("isNicknameVerified")
		self.mood = self.json.get("mood")
		self.level = self.json.get("level")
		self.notificationSubscriptionStatus = self.json.get("notificationSubscriptionStatus")
		self.pushEnabled = self.json.get("pushEnabled")
		self.membershipStatus = self.json.get("membershipStatus")
		self.content = self.json.get("content")
		self.joinedCount = self.json.get("joinedCount")
		self.role = self.json.get("role")
		self.commentsCount = self.json.get("commentsCount")
		self.aminoId = self.json.get("aminoId")
		self.comId = self.json.get("ndcId")
		self.createdTime = self.json.get("createdTime")
		self.extensions = self.json.get("extensions")
		self.storiesCount = self.json.get("storiesCount")
		self.blogsCount = self.json.get("blogsCount")


class FromCode:
	def __init__(self, data: dict = {}):
		self.json = data
		self.community = CommunityInfo(self.json.get("extensions", {}).get("community", {}))
		linkInfo = self.json.get("extensions", {}).get("linkInfo", {})

		self.path = self.json.get("path")
		self.objectId = linkInfo.get("objectId")
		self.targetCode = linkInfo.get("targetCode")
		self.comId = linkInfo.get("ndcId") or self.community.comId
		self.fullPath = linkInfo.get("fullPath")
		self.shortCode = linkInfo.get("shortCode")
		self.objectType = linkInfo.get("objectType")


class Event:
	def __init__(self, data: dict = {}):
		self.json = data
		self.comId = self.json.get("ndcId")
		self.alertOption = self.json.get("alertOption")
		self.membershipStatus = self.json.get("membershipStatus")
		self.message = Message(self.json.get("chatMessage", {}))
		self.replyMessage = Message(self.message.extensions.get("replyMessage", {}))


class Message:
	def __init__(self, data: dict = {}):
		self.json = data
		self.author = UserProfile(self.json.get("author", {}))
		self.chatId = self.json.get("threadId")
		self.mediaType = self.json.get("mediaType")
		self.mediaValue = self.json.get("mediaValue")
		self.content = self.json.get("content")
		self.clientRefId = self.json.get("clientRefId")
		self.messageId = self.json.get("messageId")
		self.userId = self.json.get("uid")
		self.createdTime = self.json.get("createdTime")
		self.messageType = self.json.get("type")
		self.isHidden = self.json.get("isHidden")
		self.includedInSummary = self.json.get("includedInSummary")
		self.extensions = self.json.get("extensions", {})
		self.originalStickerId = self.extensions.get("originalStickerId")
		self.stiker = Stiker(self.extensions.get("sticker", {}))
		self.duration = self.extensions.get("duration")
		self.chatBubbleId = self.json.get("chatBubbleId")
		self.chatBubbleVersion = self.json.get("chatBubbleVersion")



class Stiker:
	def __init__(self, data: dict = {}):
		self.json = data
		self.status = self.json.get("status")
		self.iconV2 = self.json.get("iconV2")
		self.stickerId = self.json.get("stickerId")
		self.usedCount = self.json.get("usedCount")
		self.icon = self.json.get("icon")


class Wallet:
	def __init__(self, data: dict = {}):
		self.json = data
		self.totalCoinsFloat = self.json.get("totalCoinsFloat")
		self.adsEnabled = self.json.get("adsEnabled")
		self.adsVideoStats = self.json.get("adsVideoStats")
		self.adsFlags = self.json.get("adsFlags")
		self.totalCoins = self.json.get("totalCoins")
		self.businessCoinsEnabled = self.json.get("businessCoinsEnabled")
		self.totalBusinessCoins = self.json.get("totalBusinessCoins")
		self.totalBusinessCoinsFloat = self.json.get("totalBusinessCoinsFloat")


class coinHistoryList:
	def __init__(self, data: dict = []):
		self.json = data
		self.historyList = list()
		for transaction in self.json:
			self.historyList.append(self.Transaction(transaction))

	class Transaction:
		def __init__(self, data: dict = {}):
			self.json = data
			self.taxCoinsFloat = self.json.get("taxCoinsFloat")
			self.sourceType = self.json.get("sourceType")
			self.bonusCoins = self.json.get("bonusCoins")
			self.bonusCoinsFloat = self.json.get("bonusCoinsFloat")
			self.originCoinsFloat = self.json.get("originCoinsFloat")
			self.userId = self.json.get("uid")
			self.taxCoins = self.json.get("taxCoins")
			self.changedCoinsFloat = self.json.get("changedCoinsFloat")
			self.totalCoinsFloat = self.json.get("totalCoinsFloat")
			self.extData = self.json.get("extData")
			self.isPositive = self.json.get("isPositive")
			self.createdTime = self.json.get("createdTime")
			self.totalCoins = self.json.get("totalCoins")
			self.changedCoins = self.json.get("changedCoins")
			self.originCoins = self.json.get("originCoins")


class userProfileList:
	def __init__(self, data: dict = []):
		self.json = data
		self.userProfileCount = self.json.get("userProfileCount")
		self.userProfileList = list()
		for user in self.json.get("userProfileList", []):
			self.userProfileList.append(UserProfile(user))



class communityList:
	def __init__(self, data: dict = []):
		self.json = data
		self.allItemCount = self.json.get("allItemCount")
		self.nextPageToken = self.json.get("paging", {}).get("nextPageToken")
		self.communityList = list()
		for community in self.json.get("communityList", []):
			self.communityList.append(CommunityInfo(community))


class CommunityInfo:
	def __init__(self, data: dict = []):
		self.json = data
		self.userAddedTopicList = self.json.get("userAddedTopicList")
		self.agent = UserProfile(self.json.get("agent")) if self.json.get("agent") else None
		self.listedStatus = self.json.get("listedStatus")
		self.probationStatus = self.json.get("probationStatus")
		self.themePack = self.json.get("themePack")
		self.membersCount = self.json.get("membersCount")
		self.primaryLanguage = self.json.get("primaryLanguage")
		self.communityHeat = self.json.get("communityHeat")
		self.tagline = self.json.get("tagline")
		self.joinType = self.json.get("joinType")
		self.status = self.json.get("status")
		self.modifiedTime = self.json.get("modifiedTime")
		self.comId = self.json.get("ndcId")
		self.activeInfo = self.json.get("activeInfo")
		self.promotionalMediaList = self.json.get("activeInfo")
		self.icon = self.json.get("icon")
		self.link = self.json.get("link")
		self.updatedTime = self.json.get("updatedTime")
		self.endpoint = self.json.get("endpoint")
		self.name = self.json.get("name")
		self.templateId = self.json.get("templateId")
		self.createdTime = self.json.get("createdTime")




class ThreadList:
	def __init__(self, data: dict = []):
		self.json = data
		self.chats = list()
		for chat in self.json:
			if isinstance(chat, dict):
				self.chats.append(Thread(chat))


class Thread:
	def __init__(self, data: dict = []):
		self.json = data
		self.userAddedTopicList = self.json.get("userAddedTopicList", [])
		self.membersQuota = self.json.get("membersQuota")
		self.membersSummary = list()
		self.chatId = self.json.get("threadId")
		self.keywords = self.json.get("keywords")
		self.membersCount = self.json.get("membersCount")
		self.strategyInfo = self.json.get("strategyInfo")
		self.isPinned = self.json.get("isPinned")
		self.title = self.json.get("title")
		self.membershipStatus = self.json.get("membershipStatus")
		self.content = self.json.get("content")
		self.needHidden = self.json.get("needHidden")
		self.alertOption = self.json.get("alertOption")
		self.lastReadTime = self.json.get("lastReadTime")
		self.type = self.json.get("type")
		self.status = self.json.get("status")
		self.modifiedTime = self.json.get("modifiedTime")
		self.lastMessageSummary = Message(self.json.get("lastMessageSummary", {}))
		self.condition = self.json.get("condition")
		self.icon = self.json.get("icon")
		self.latestActivityTime = self.json.get("latestActivityTime")
		self.author = UserProfile(self.json.get("author", {}))
		self.extensions = self.json.get("extensions", {})
		self.comId = self.json.get("ndcId")
		self.createdTime = self.json.get("createdTime")

		for member in self.json.get("membersSummary", []):
			self.membersSummary.append(UserProfile(member))



class MessageList:
	def __init__(self, data: dict = []):
		self.json = data
		paging = self.json.get("paging", {})
		
		self.messages = list()
		self.nextPageToken = paging.get("nextPageToken")
		self.prevPageToken = paging.get("prevPageToken")
		for message in self.json.get("messageList", []):
			self.messages.append(Message(message))