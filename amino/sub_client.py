from amino.helpers.requester import Requester
from amino.api.sync.sub import *
from amino import MediaObject
from typing import BinaryIO

class _Client:
	def upload_media(self, file: BinaryIO, fileType: str | None = None) -> MediaObject: ...
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
	comId: str | None = None
	def __init__(self, client: _Client):
		self.req: Requester = client.req
		self.upload_media = client.upload_media