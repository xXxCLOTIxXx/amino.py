from .base_object import BaseObject

class MediaObject(BaseObject):
	"""
	media object returned by the upload_media function

	"""
	
	def __init__(self, data: dict):
		super().__init__(data)
		self.mediaValue: dict | None = data.get("mediaValue")