from amino.api.base import BaseClass
from amino import SpecifyType, WrongType, UnsupportedLanguage, Blog, BaseObject, Wiki


class GlobalBlogsModule(BaseClass):
	

	def get_supported_languages(self) -> list[str]: ...

	def get_blog_info(self, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None) -> Wiki | Blog | BaseObject:
		"""
		Getting blog info.

		**Parameters**:
		- blogId: Id of the blog
		- wikiId:  Id of the wiki
		- quizId:  Id of the quiz
		- fileId:  Id of the file
			- if all fields are None, exception will be raised
			- if more than one field not empty, it will return only one object using priority like this:
				- quizId -> blogId -> wikiId -> fileId
		"""
		if blogId or quizId:
			return Blog(self.req.make_sync_request("GET", f"/g/s/blog/{quizId if quizId is not None else blogId}").json())
		if wikiId:
			return Wiki(self.req.make_sync_request("GET", f"/g/s/item/{wikiId}").json())
		if fileId:
			return BaseObject(self.req.make_sync_request("GET", f"/g/s/shared-folder/files/{fileId}").json())
		raise SpecifyType()


	def like_blog(self, blogId: str | list | None = None, wikiId: str | None = None) -> BaseObject:
		"""
		Like a Blog, Multiple Blogs or a Wiki.

		**Parameters**
		- blogId : ID of the Blog or List of IDs of the Blogs. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""

		data: dict = {
			"value": 4,

		}

		if blogId:
			if isinstance(blogId, str):
				data["eventSource"] = "UserProfileView"
				url = f"/g/s/blog/{blogId}/g-vote?cv=1.2"
			elif isinstance(blogId, list):
				data["targetIdList"] = blogId
				url = f"/g/s/feed/g-vote"
			else: raise WrongType(type(blogId))
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/g/s/item/{wikiId}/g-vote?cv=1.2"
		else: raise SpecifyType
		
		return BaseObject(self.req.make_sync_request("POST", url, data).json())
	

	def unlike_blog(self, blogId: str | None = None, wikiId: str | None = None) -> BaseObject:
		"""
		Remove a like from a Blog or Wiki.

		**Parameters**
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
		
		if blogId:url = f"/g/s/blog/{blogId}/g-vote?eventSource=UserProfileView"
		elif wikiId:url = f"/g/s/item/{wikiId}/g-vote?eventSource=PostDetailView"
		else:raise SpecifyType

		return BaseObject(self.req.make_sync_request("DELETE", url).json())


	def get_ta_announcements(self, language: str = "en", start: int = 0, size: int = 25) -> list[Blog]:
		"""
		Get the list of Team Amino's Announcement Blogs.

		**Parameters**
		- language : Language of the Blogs.
			- ``client.get_supported_languages()``
			- ``en``, ``es``, ``ru``, ``fr``, ...
		- start : Where to start the list.
		- size : Size of the list.
		"""
		if language not in self.get_supported_languages():raise UnsupportedLanguage(language)
		result = self.req.make_sync_request("GET", f"/g/s/announcement?language={language}&start={start}&size={size}").json()["blogList"]

		return [Blog(x) for x in result]
