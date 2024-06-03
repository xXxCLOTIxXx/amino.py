from typing import Optional
from .user_profile import UserProfile
from .community import Community

class StickerCollection:
	__slots__ = (
		"data", "author", "status", "collectionType", "modifiedTime", "bannerUrl",
		"smallIcon", "stickersCount", "usedCount", "icon", "title", "collectionId",
		"isActivated", "ownershipStatus", "isNew", "availableComIds", "description",
		"extensions", "iconSourceStickerId", "originalAuthor", "originalCommunity",
		"restrictionInfo", "discountStatus", "discountValue", "ownerId", "ownerType",
		"restrictType", "restrictValue", "availableDuration"
	)
	def __init__(self, data: dict):
		if not data:
			for attr in self.__slots__:
				setattr(self, attr, None)
			return

		self.data: dict = data

		self.author = UserProfile(data.get("author"))

		self.status = data.get("status")
		self.collectionType = data.get("collectionType")
		self.modifiedTime = data.get("modifiedTime")
		self.bannerUrl = data.get("bannerUrl")
		self.smallIcon = data.get("smallIcon")
		self.stickersCount = data.get("stickersCount")
		self.usedCount = data.get("usedCount")
		self.icon = data.get("icon")
		self.title = data.get("name")
		self.collectionId = data.get("collectionId")

		self.isActivated = data.get("isActivated")
		self.ownershipStatus = data.get("ownershipStatus")
		self.isNew = data.get("isNew")
		self.availableComIds = data.get("availableNdcIds")
		self.description = data.get("description")

		#extensions
		self.extensions = data.get("extensions", {})
		self.iconSourceStickerId = self.extensions.get("iconSourceStickerId")
		self.originalAuthor = UserProfile(self.extensions.get("originalAuthor"))
		self.originalCommunity = Community(self.extensions.get("originalCommunity"))

		#restrictionInfo
		self.restrictionInfo = data.get("restrictionInfo", {})
		self.discountStatus = self.restrictionInfo.get("discountStatus")
		self.discountValue = self.restrictionInfo.get("discountValue")
		self.ownerId = self.restrictionInfo.get("ownerUid")
		self.ownerType = self.restrictionInfo.get("ownerType")
		self.restrictType = self.restrictionInfo.get("restrictType")
		self.restrictValue = self.restrictionInfo.get("restrictValue")
		self.availableDuration = self.restrictionInfo.get("availableDuration")
	


class Sticker:
	__slots__ = (
		"data", "collection", "status", "icon", "iconV2", "name", "stickerId",
		"smallIcon", "smallIconV2", "stickerCollectionId", "mediumIcon",
		"mediumIconV2", "extensions", "usedCount", "createdTime"
	)

	def __init__(self, data: dict = None):
		if not data:
			for attr in self.__slots__:
				setattr(self, attr, None)
			return

		self.data = data

		self.collection = StickerCollection(data.get("stickerCollectionSummary"))

		self.status: Optional[str] = data.get("status")
		self.icon: Optional[str] = data.get("icon")
		self.iconV2: Optional[str] = data.get("iconV2")
		self.name: Optional[str] = data.get("name")
		self.stickerId: Optional[str] = data.get("stickerId")
		self.smallIcon: Optional[str] = data.get("smallIcon")
		self.smallIconV2: Optional[str] = data.get("smallIconV2")
		self.stickerCollectionId: Optional[str] = data.get("stickerCollectionId")
		self.mediumIcon: Optional[str] = data.get("mediumIcon")
		self.mediumIconV2: Optional[str] = data.get("mediumIconV2")
		self.extensions: Optional[str] = data.get("extensions")
		self.usedCount: Optional[str] = data.get("usedCount")
		self.createdTime: Optional[str] = data.get("createdTime")