from .sticker import Sticker
from .user_profile import UserProfile

class Message:
	__slots__ = (
		"data", "author", "sticker", "content",
		"includedInSummary", "isHidden", "messageType", "messageId", "mediaType",
		"mediaValue", "chatBubbleId", "clientRefId", "chatId", "createdTime",
		"chatBubbleVersion", "type", "extensions", "replyMessage", "mentionUserIds", "duration",
		"originalStickerId", "videoExtensions", "videoDuration", "videoHeight",
		"videoWidth", "videoCoverImage", "tippingCoins"
	)
	
	def __init__(self, data: dict):
		if not data:
			for attr in self.__slots__:
				setattr(self, attr, None)
			return
		self.data=data
		self.author = UserProfile(data.get("author"))

		extensions = data.get("extensions") or {}
		videoExtensions = extensions.get("videoExtensions") or {}

		self.sticker = Sticker(extensions.get("sticker"))

		self.content = data.get("content")
		self.includedInSummary = data.get("includedInSummary")
		self.isHidden = data.get("isHidden")
		self.messageId = data.get("messageId")
		self.messageType = data.get("messageType")
		self.mediaType = data.get("mediaType")
		self.chatBubbleId = data.get("chatBubbleId")
		self.clientRefId = data.get("clientRefId")
		self.chatId = data.get("threadId")
		self.createdTime = data.get("createdTime")
		self.chatBubbleVersion = data.get("chatBubbleVersion")
		self.type = data.get("type")
		self.replyMessage = extensions.get("replyMessage")
		self.mediaValue = data.get("mediaValue")
		self.extensions = extensions
		self.duration = extensions.get("duration")
		self.videoDuration = videoExtensions.get("duration")
		self.videoHeight = videoExtensions.get("height")
		self.videoWidth = videoExtensions.get("width")
		self.videoCoverImage = videoExtensions.get("coverImage")
		self.originalStickerId = extensions.get("originalStickerId")
		self.mentionUserIds = tuple(m.get("uid") for m in extensions.get("mentionedArray", ()))
		self.tippingCoins = extensions.get("tippingCoins")
