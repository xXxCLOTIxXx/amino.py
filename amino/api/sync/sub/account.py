from amino.api.base import BaseClass
from amino import MediaObject, BaseObject
from typing import BinaryIO

class CommunityAccountModule(BaseClass):
	comId: str | int | None
	def upload_media(self, file: BinaryIO, fileType: str | None = None) -> MediaObject: ...


	def edit_profile(self, nickname: str | None = None, content: str | None = None, icon: BinaryIO | None = None, chatRequestPrivilege: str | None = None, imageList: list | None = None, captionList: list | None = None, backgroundImage: str | None = None, backgroundColor: str | None = None, titles: list | None = None, colors: list | None = None, defaultBubbleId: str | None = None, comId: str | int | None = None) -> BaseObject:
		"""
		Edit account's Profile.

		**Parameters**
		- nickname : Nickname of the Profile.
		- content : Biography of the Profile.
		- icon : Icon of the Profile.
		- titles : Titles.
		- colors : Colors for titles.
		- imageList : List of images.
		- captionList : Captions for images.
		- backgroundImage : Url of the Background Picture of the Profile.
		- backgroundColor : Hexadecimal Background Color of the Profile.
		- defaultBubbleId : Chat bubble ID.
		- chatRequestPrivilege : Manage your right to accept chats.
		"""

		mediaList = []
		data = {}
		if captionList and imageList:
			for image, caption in zip(imageList, captionList):
				mediaList.append([100, self.upload_media(image).mediaValue, caption])
		else:
			if imageList is not None:
				for image in imageList:
					mediaList.append([100, self.upload_media(image).mediaValue, None])

		if imageList is not None or captionList is not None:data["mediaList"] = mediaList
		if nickname:data["nickname"] = nickname
		if icon:data["icon"] = self.upload_media(icon).mediaValue
		if content:data["content"] = content
		if chatRequestPrivilege:data["extensions"] = {"privilegeOfChatInviteRequest": chatRequestPrivilege}
		if backgroundImage:
			data["extensions"] = {"style": {
				"backgroundMediaList": [[100, backgroundImage, None, None, None]]
				}}
		if backgroundColor:data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if defaultBubbleId:data["extensions"] = {"defaultBubbleId": defaultBubbleId}
		if titles and colors:
			tlt = []
			for titles, colors in zip(titles, colors):
				tlt.append({"title": titles, "color": colors})
			data["extensions"] = {"customTitles": tlt}

		return BaseObject(self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/user-profile/{self.userId}", data).json())



	def activity_status(self, status: bool, comId: str | int | None = None) -> BaseObject:
		"""
		Sets your activity status to offline or online.

		**Parameters**
		- status: bool
			- True: online
			- False: offline
		"""
		data = {
			"onlineStatus": 1 if status is True else 2,
			"duration": 86400
		}

		return BaseObject(self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/user-profile/{self.userId}/online-status", data).json())
