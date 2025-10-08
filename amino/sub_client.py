from amino.helpers.requester import Requester
from amino.api.sync.sub import *
from amino import MediaObject, FromCode
from typing import BinaryIO

class _Client:
	def upload_media(self, file: BinaryIO, fileType: str | None = None) -> MediaObject: ...
	def get_from_link(self, link: str) -> FromCode: ...
	req: Requester

class SubClient(
	CommunityAccountModule,
	ACMModule,
	CommunityModeratorModule,
	CommunityBlogsModule,
	CommunityChatsModule,
	CommunityCommentsModule,
	CommunityNotificationsModule,
	CommunityOtherModule,
	CommunityStickersModule,
	CommunityUsersModule
):
	comId: str | int | None = None
	def __init__(self, client: _Client, comId: str | int | None = None, aminoId: str | None = None):
		self.req: Requester = client.req
		if comId: self.comId = comId
		elif aminoId:
			link = f"http://aminoapps.com/c/{aminoId}"
			self.comId = client.get_from_link(link).comId
		self.upload_media = client.upload_media