from amino.api.base import BaseClass
from amino import SpecifyType, args

class CommunityCommentsModule(BaseClass):
	comId: str | int | None


	def comment(self, message: str, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None, replyTo: str | None = None, isGuest: bool | None = False, comId: str | int | None = None):
		"""
		Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- message : Message to be sent.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		- replyTo : ID of the Comment to Reply to.
		- isGuest : You want to be Guest or no?
		"""
		data = {
			"content": message,
			"stickerId": None,
			"type": 0
		}
		if replyTo: data["respondTo"] = replyTo
		if isGuest: comType = "g-comment"
		else: comType = "comment"

		if userId:
			data["eventSource"] = "UserProfileView"
			url = f"/x{comId or self.comId}/s/user-profile/{userId}/{comType}"
		elif blogId:
			data["eventSource"] = "PostDetailView"
			url = f"/x{comId or self.comId}/s/blog/{blogId}/{comType}"
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/x{comId or self.comId}/s/item/{wikiId}/{comType}"
		else: raise SpecifyType

		return self.req.make_sync_request("POST",  url, data).json()

					  
	def delete_comment(self, commentId: str, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None, comId: str | int | None = None):
		"""
		Delete a Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- commentId : ID of the Comment.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
		if userId:url = f"/x{comId or self.comId}/s/user-profile/{userId}/comment/{commentId}"
		elif blogId:url = f"/x{comId or self.comId}/s/blog/{blogId}/comment/{commentId}"
		elif wikiId:url = f"/x{comId or self.comId}/s/item/{wikiId}/comment/{commentId}"
		else:raise SpecifyType

		return self.req.make_sync_request("DELETE",  url).json()

	def like_comment(self, commentId: str | None, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None, comId: str | int | None = None):
		"""
		Like a Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- commentId : ID of the Comment.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
		data: dict = {"value": 1}

		if userId:
			data["eventSource"] = "UserProfileView"
			url = f"/x{comId or self.comId}/s/user-profile/{userId}/comment/{commentId}/vote?cv=1.2&value=1"
		elif blogId:
			data["eventSource"] = "PostDetailView"
			url = f"/x{comId or self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1"
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/x{comId or self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?cv=1.2&value=1"
		else:raise SpecifyType

		return self.req.make_sync_request("POST",  url, data).json()

	def unlike_comment(self, commentId: str, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None, comId: str | int | None = None):
		"""
		Remove a like from a Comment on a User's Wall, Blog or Wiki.

		**Parameters**
		- commentId : ID of the Comment.
		- userId : ID of the User. (for Walls)
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
		if userId:url = f"/x{comId or self.comId}/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView"
		elif blogId:url = f"/x{comId or self.comId}/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		elif wikiId:url = f"/x{comId or self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		else:raise SpecifyType

		return self.req.make_sync_request("DELETE",  url).json()

	def upvote_comment(self, blogId: str, commentId: str, comId: str | int | None = None):
		"""
		Upvote comment on question.

		**Parameters**
		- blogId : ID of the Blog.
		- commentId : ID of the Comment.
		"""
		data = {
			"value": 1,
			"eventSource": "PostDetailView"
		}

		return self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1", data).json()

	def downvote_comment(self, blogId: str, commentId: str, comId: str | int | None = None):
		"""
		Downvote comment on question.

		**Parameters**
		- blogId : ID of the Blog.
		- commentId : ID of the Comment.
		"""
		data = {
			"value": -1,
			"eventSource": "PostDetailView"
		}

		return self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1", data).json()

	def unvote_comment(self, blogId: str, commentId: str, comId: str | int | None = None):
		"""
		Remove vote from comment.

		**Parameters**
		- blogId : ID of the Blog.
		- commentId : ID of the Comment.
		"""
		return self.req.make_sync_request("DELETE",  f"/x{comId or self.comId}/s/blog/{blogId}/comment/{commentId}/vote?eventSource=PostDetailView").json()

	def reply_wall(self, userId: str, commentId: str, message: str, comId: str | int | None = None):
		"""
		Reply to comment on wall.

		**Parameters**
		- userId : ID of the User.
		- commentId : ID of the Comment.
		- message : Message.
		"""
		data = {
			"content": message,
			"stackedId": None,
			"respondTo": commentId,
			"type": 0,
			"eventSource": "UserProfileView"
		}

		return self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/user-profile/{userId}/comment", data).json()

	def get_wall_comments(self, userId: str, sorting: str = args.Sorting.Newest, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		List of Wall Comments of an User.

		**Parameters**
		- userId: user id
		- start : Where to start the list.
		- size : Size of the list.
		- sorting : sorting comments (use ``amino.arguments.Sorting. some``)
		"""
		if sorting not in args.Sorting.all:raise ValueError(f"Sorting.all: {sorting} not in {args.Sorting.all}")
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/user-profile/{userId}/comment?sort={sorting}&start={start}&size={size}").json()["commentList"]
