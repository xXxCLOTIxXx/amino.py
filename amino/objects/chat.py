from .base_object import BaseObject
from . import Community, UserProfile

class Message(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)

        if data.get("message") is not None: data = data.get("message", {})

        self.author: UserProfile = UserProfile(self.data.get("author", {}))

        extensions = self.data.get("extensions", {})
        self.extensions = extensions

        self.sticker: Sticker = Sticker(extensions.get("sticker", {}))

        self.content = self.data.get("content")
        self.includedInSummary = self.data.get("includedInSummary")
        self.isHidden = self.data.get("isHidden")
        self.messageId = self.data.get("messageId")
        self.messageType = self.data.get("messageType")
        self.mediaType = self.data.get("mediaType")
        self.mediaValue = self.data.get("mediaValue")
        self.chatBubbleId = self.data.get("chatBubbleId")
        self.clientRefId = self.data.get("clientRefId")
        self.chatId = self.data.get("threadId")
        self.createdTime = self.data.get("createdTime")
        self.chatBubbleVersion = self.data.get("chatBubbleVersion")
        self.type = self.data.get("type")
        self.replyMessage = extensions.get("replyMessage")
        self.duration = extensions.get("duration")
        self.originalStickerId = extensions.get("originalStickerId")
        self.tippingCoins = extensions.get("tippingCoins")

        video_ext = extensions.get("videoExtensions", {})
        self.videoExtensions = video_ext
        self.videoDuration = video_ext.get("duration")
        self.videoHeight = video_ext.get("height")
        self.videoWidth = video_ext.get("width")
        self.videoCoverImage = video_ext.get("coverImage")

        mentioned_array = extensions.get("mentionedArray", [])
        self.mentionUserIds = [m.get("uid") for m in mentioned_array if isinstance(m, dict)]


class Sticker(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)

        self.collection: StickerCollection = StickerCollection(self.data.get("stickerCollectionSummary", {}))

        self.status = self.data.get("status")
        self.icon = self.data.get("icon")
        self.iconV2 = self.data.get("iconV2")
        self.name = self.data.get("name")
        self.stickerId = self.data.get("stickerId")
        self.smallIcon = self.data.get("smallIcon")
        self.smallIconV2 = self.data.get("smallIconV2")
        self.stickerCollectionId = self.data.get("stickerCollectionId")
        self.mediumIcon = self.data.get("mediumIcon")
        self.mediumIconV2 = self.data.get("mediumIconV2")
        self.extensions = self.data.get("extensions")
        self.usedCount = self.data.get("usedCount")
        self.createdTime = self.data.get("createdTime")


class StickerCollection(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)

        self.author: UserProfile = UserProfile(self.data.get("author", {}))

        extensions = self.data.get("extensions", {})
        self.extensions = extensions

        self.originalAuthor: UserProfile = UserProfile(extensions.get("originalAuthor", {}))
        self.originalCommunity: Community = Community(extensions.get("originalCommunity", {}))

        self.status = self.data.get("status")
        self.collectionType = self.data.get("collectionType")
        self.modifiedTime = self.data.get("modifiedTime")
        self.bannerUrl = self.data.get("bannerUrl")
        self.smallIcon = self.data.get("smallIcon")
        self.stickersCount = self.data.get("stickersCount")
        self.usedCount = self.data.get("usedCount")
        self.icon = self.data.get("icon")
        self.title = self.data.get("name")
        self.collectionId = self.data.get("collectionId")
        self.isActivated = self.data.get("isActivated")
        self.ownershipStatus = self.data.get("ownershipStatus")
        self.isNew = self.data.get("isNew")
        self.availableComIds = self.data.get("availableNdcIds")
        self.description = self.data.get("description")

        self.iconSourceStickerId = extensions.get("iconSourceStickerId")

        restriction = self.data.get("restrictionInfo", {})
        self.restrictionInfo = restriction
        self.discountStatus = restriction.get("discountStatus")
        self.discountValue = restriction.get("discountValue")
        self.ownerId = restriction.get("ownerUid")
        self.ownerType = restriction.get("ownerType")
        self.restrictType = restriction.get("restrictType")
        self.restrictValue = restriction.get("restrictValue")
        self.availableDuration = restriction.get("availableDuration")


class Chat(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)
        if data.get("thread") is not None: data = data.get("thread", {})

        self.author: UserProfile = UserProfile(self.data.get("author", {}))
        self.membersSummary: list[UserProfile] = [UserProfile(x) for x in self.data.get("membersSummary", [])]

        self.userAddedTopicList = self.data.get("userAddedTopicList")
        self.membersQuota = self.data.get("membersQuota")
        self.chatId = self.data.get("threadId")
        self.keywords = self.data.get("keywords")
        self.membersCount = self.data.get("membersCount")
        self.isPinned = self.data.get("isPinned")
        self.title = self.data.get("title")
        self.membershipStatus = self.data.get("membershipStatus")
        self.content = self.data.get("content")
        self.needHidden = self.data.get("needHidden")
        self.alertOption = self.data.get("alertOption")
        self.lastReadTime = self.data.get("lastReadTime")
        self.type = self.data.get("type")
        self.status = self.data.get("status")
        self.publishToGlobal = self.data.get("publishToGlobal")
        self.modifiedTime = self.data.get("modifiedTime")
        self.condition = self.data.get("condition")
        self.icon = self.data.get("icon")
        self.latestActivityTime = self.data.get("latestActivityTime")
        self.comId = self.data.get("ndcId")
        self.createdTime = self.data.get("createdTime")

        extensions = self.data.get("extensions", {})
        self.extensions = extensions

        self.viewOnly = extensions.get("viewOnly")
        self.coHosts = extensions.get("coHost")
        self.membersCanInvite = extensions.get("membersCanInvite")
        self.language = extensions.get("language")
        self.announcement = extensions.get("announcement")
        self.backgroundImage = None
        try:
            self.backgroundImage = extensions.get("bm", [None, None])[1]
        except (TypeError, IndexError):
            pass

        self.lastMembersSummaryUpdateTime = extensions.get("lastMembersSummaryUpdateTime")
        self.channelType = extensions.get("channelType")
        self.creatorId = extensions.get("creatorUid")
        self.bannedUsers = extensions.get("bannedMemberUidList")
        self.visibility = extensions.get("visibility")
        self.fansOnly = extensions.get("fansOnly")
        self.pinAnnouncement = extensions.get("pinAnnouncement")
        self.vvChatJoinType = extensions.get("vvChatJoinType")
        self.disabledTime = extensions.get("__disabledTime__")
        self.tippingPermStatus = extensions.get("tippingPermStatus")
        self.screeningRoomHostId = extensions.get("screeningRoomHostUid")

        screening_permission = extensions.get("screeningRoomPermission", {})
        self.screeningRoomPermission = screening_permission.get("action")

        organizer_transfer = extensions.get("organizerTransferRequest", {})
        self.organizerTransferCreatedTime = organizer_transfer.get("createdTime")
        self.organizerTransferId = organizer_transfer.get("requestId")


class ChatMessages:
    def __init__(self, data: dict):
        self.data = data

        self.messageList: list[Message] = [Message(x) for x in data.get("messageList", [])]
        self.nextPageToken = data.get("paging", {}).get("nextPageToken")
        self.prevPageToken = data.get("paging", {}).get("prevPageToken")