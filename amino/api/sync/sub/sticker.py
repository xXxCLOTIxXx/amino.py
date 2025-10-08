from amino.api.base import BaseClass

class CommunityStickersModule(BaseClass):
	comId: str | int | None

	def get_sticker_pack_info(self, sticker_pack_id: str, comId: str | int | None = None):
		"""
		Getting all info about sticker pack.

		**Parameters**
		- sticker_pack_id: id of the sticker pack
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/sticker-collection/{sticker_pack_id}?includeStickers=true").json()["stickerCollection"]

	def get_my_sticker_packs(self, comId: str | int | None = None):
		"""
		Getting sticker packs in account.

		**Parameters**
		- sticker_pack_id: id of the sticker pack
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/sticker-collection?includeStickers=false&type=my-active-collection").json()["stickerCollection"]



	def get_store_stickers(self, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Getting all available stickers from store.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/store/items?sectionGroupId=sticker&start={start}&size={size}").json()

	def get_community_stickers(self, comId: str | int | None = None):
		"""
		Getting all available stickers in community.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/sticker-collection?type=community-shared").json()

	def get_sticker_collection(self, collectionId: str, comId: str | int | None = None):
		"""
		Getting all available info about sticker pack.

		**Parameters**
		- collectionId: id of the collection
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/sticker-collection/{collectionId}?includeStickers=true").json()["stickerCollection"]
