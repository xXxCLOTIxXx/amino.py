class UploadType:
	"""
	file types to upload to amino servers

	attributes:
	
	- audio
	- image_jpg
	- gif
	- image_png

	- all (list of all attributes)

	"""
	
	audio: str = "audio/aac"
	image_jpg: str = "image/jpg"
	gif: str = "image/gif"
	image_png: str = "image/png"
	all: list = [audio, image_jpg, gif, image_png]