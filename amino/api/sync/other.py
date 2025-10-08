from amino.api.base import BaseClass
from amino import FromCode
from amino import SpecifyType
from amino import BaseObject, LinkIdentify
from amino import args
from amino import SpecifyType
from amino import MediaObject

from typing import BinaryIO
from mimetypes import guess_type



class GlobalOtherModule(BaseClass):

	def link_identify(self, code: str) -> LinkIdentify:
		"""
		Getting info about invite from code. 

		**Parameters**:
		- code: str
			- *code* is thing *after* http://aminoapps.com/invite/
		"""
		return LinkIdentify(self.req.make_sync_request("GET", f"/g/s/community/link-identify?q=http%3A%2F%2Faminoapps.com%2Finvite%2F{code}").json())

	def get_supported_languages(self) -> list[str]:
		"""
		Get the List of Supported Languages by Amino.
		"""
		return self.req.make_sync_request("GET", f"/g/s/community-collection/supported-languages?start=0&size=100").json()["supportedLanguages"]

	def get_from_id(self, objectId: str, objectType: int, comId: int | None = None) -> FromCode:
		"""
		Get the Object Information from the Object ID and Type.

		**Parameters**
		- objectID : ID of the Object. User ID, Blog ID, etc.
		- objectType : Type of the Object.
		- comId : ID of the Community. Use if the Object is in a Community.
		"""
		data = {
			"objectId": objectId,
			"targetCode": 1,
			"objectType": objectType,
		}

		return FromCode(self.req.make_sync_request("POST", f"/g/{f's-x{comId}' if comId else 's'}/link-resolution", data).json())

	def get_from_link(self, link: str) -> FromCode:
		"""
		Get the Object Information from the Amino URL.

		**Parameters**
		- link : link from the Amino.
			- ``http://aminoapps.com/p/EXAMPLE``, the ``link`` is 'EXAMPLE'.
		"""
		return FromCode(self.req.make_sync_request("GET", f"/g/s/link-resolution?q={link}").json())

	def get_from_deviceid(self, deviceId: str) -> str:
		"""
		Get the User ID from an Device ID.

		**Parameters**
		- deviceID : ID of the Device.
		"""
		return self.req.make_sync_request("GET", f"/g/s/auid?deviceId={deviceId}").json()["auid"]

	def flag(self, reason: str, flagType: int, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None, asGuest: bool = False) -> BaseObject:
		"""
		Flag a User, Blog or Wiki.

		**Parameters**
		- reason : Reason of the Flag.
		- flagType : Type of the Flag.
		- userId : ID of the User.
		- blogId : ID of the Blog.
		- wikiId : ID of the Wiki.
		- asGuest : Execute as a Guest.
		"""
		data = {
			"flagType": flagType,
			"message": reason,
		}
		if userId:
			data["objectId"] = userId
			data["objectType"] = 0
		elif blogId:
			data["objectId"] = blogId
			data["objectType"] = 1
		elif wikiId:
			data["objectId"] = wikiId
			data["objectType"] = 2
		else:raise SpecifyType
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/{'g-flag' if asGuest else 'flag'}", data).json())




	def upload_media(self, file: BinaryIO, fileType: str | None = None) -> MediaObject:
		"""
        Upload file to the amino servers.

        **Parameters**
        - file : File to be uploaded.
		"""
		if fileType is None:
			fileType = guess_type(file.name)[0]
		if fileType not in args.UploadType.all: raise SpecifyType(fileType)
		return MediaObject(self.req.make_sync_request("POST", "/g/s/media/upload", file.read(), content_type=fileType).json())
