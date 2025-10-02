from amino.api.base import BaseClass
from amino import SpecifyType, WrongType
from amino import args, BaseObject, Comment

class GlobalCommentsModule(BaseClass):
	

	def get_wall_comments(self, userId: str, sorting: str = args.Sorting.Newest, start: int = 0, size: int = 25) -> list[Comment]:
		"""
		List of Wall Comments of an User.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		- sorting: Type of sorting of received objects
		"""
		if sorting not in args.Sorting.all:raise WrongType(sorting)
		result =  self.req.make_sync_request("GET", f"/g/s/user-profile/{userId}/g-comment?sort={sorting}&start={start}&size={size}").json()["commentList"]
		return [Comment(x) for x in result]

	def get_blog_comments(self, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None, sorting: str = args.Sorting.Newest, start: int = 0, size: int = 25) -> list[Comment]:
		"""
		Getting blog info.

		**Parameters**:
		- start : Where to start the list.
		- size : Size of the list.
		- sorting: Type of sorting of received objects
		- blogId: Id of the blog
		- wikiId:  Id of the wiki
		- quizId:  Id of the quiz
		- fileId:  Id of the file
			- if all fields are None, exception will be raised
			- if more than one field not empty, it will return only one object using priority like this:
				- blogId -> quizId -> wikiId -> fileId
		"""
		if sorting not in args.Sorting.all:raise WrongType(sorting)
		if blogId or quizId:url = f"/g/s/blog/{quizId if not blogId else blogId}/comment"
		elif wikiId:url = f"/g/s/item/{wikiId}/comment"
		elif fileId:url = f"/g/s/shared-folder/files/{fileId}/comment"
		else:raise SpecifyType
		result = self.req.make_sync_request("GET", f"{url}?sort={sorting}&start={start}&size={size}").json()["commentList"]
		return [Comment(x) for x in result]

	def comment(self, message: str, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None, replyTo: str | None = None, stickerId: str | None = None) -> BaseObject:
		"""
		Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- message : Message to be sent.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		- replyTo : ID of the Comment to Reply to.
		- stickerId: ID of the sticker
		"""
		data = {
			"content": message,
			"stickerId": None,
			"type": 0,
		}


		if stickerId:
			data["content"] = None
			data["stickerId"] = stickerId
			data["type"] = 3
		if replyTo:
			data["respondTo"] = replyTo
		if userId:
			data["eventSource"] = "UserProfileView"
			url = f"/g/s/user-profile/{userId}/g-comment"
		elif blogId:
			data["eventSource"] = "PostDetailView"
			url = f"/g/s/blog/{blogId}/g-comment"
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/g/s/item/{wikiId}/g-comment"
		else: raise SpecifyType

		return BaseObject(self.req.make_sync_request("POST", url, data).json())


	def delete_comment(self, commentId: str, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None) -> BaseObject:
		"""
		Delete a Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- commentId : ID of the Comment.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
		if userId:url = f"/g/s/user-profile/{userId}/g-comment/{commentId}"
		elif blogId:url = f"/g/s/blog/{blogId}/g-comment/{commentId}"
		elif wikiId:url = f"/g/s/item/{wikiId}/g-comment/{commentId}"
		else:raise SpecifyType

		return BaseObject(self.req.make_sync_request("DELETE", url).json())


	def like_comment(self, commentId: str, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None) -> BaseObject:
		"""
		Like a Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- commentId : ID of the Comment.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
		data = {
			"value": 4,
			"eventSource": ""
		}
		if userId:
			data["eventSource"] = "UserProfileView"
			url = f"/g/s/user-profile/{userId}/comment/{commentId}/g-vote?cv=1.2&value=1"
		elif blogId:
			data["eventSource"] = "PostDetailView"
			url = f"/g/s/blog/{blogId}/comment/{commentId}/g-vote?cv=1.2&value=1"
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/g/s/item/{wikiId}/comment/{commentId}/g-vote?cv=1.2&value=1"
		else: raise SpecifyType

		return BaseObject(self.req.make_sync_request("POST", url, data).json())

	def unlike_comment(self, commentId: str, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None) -> BaseObject:
		"""
		Remove a like from a Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- commentId : ID of the Comment.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
		if userId:url = f"/g/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView"
		elif blogId:url = f"/g/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		elif wikiId:url = f"/g/s/item/{wikiId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		else:raise SpecifyType
		
		return BaseObject(self.req.make_sync_request("DELETE", url).json())