
class MediaObject:
	"""
	media object returned by the upload_media function

	attributes:
	
	- data
	- mediaValue

	"""
	 
	__slots__ = ("json", "mediaValue")
	
	def __init__(self, data: dict):
		if not data:
			for attr in self.__slots__:
				setattr(self, attr, None)
			return
		
		self.json = data
		self.mediaValue = data.get("mediaValue")