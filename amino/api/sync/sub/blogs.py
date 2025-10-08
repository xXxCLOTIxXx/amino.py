from amino.api.base import BaseClass
from amino import SpecifyType, WrongType, args, MediaObject
from typing import BinaryIO

class CommunityBlogsModule(BaseClass):
	comId: str | int | None
	def upload_media(self, file: BinaryIO, fileType: str | None = None) -> MediaObject: ...

	def post_blog(self, title: str, content: str, imageList: list | None = None, captionList: list | None = None, categoriesList: list | None = None, backgroundColor: str | None = None, fansOnly: bool = False, extensions: dict | None = None, comId: str | int | None = None):
		"""
		Posting blog.

		**Parameters**:
		- title: str
		- content: str
		- imageList: list = None
		- captionList: list = None
			- captions for images
		- categoriesList: list = None
		- backgroundColor: str = None
			- should be only hex code, like "#000000"
			- if None, it will be just white
		- fansOnly: bool = False
			- is it for your onlyfans or no?
			- works only if you have fanclub
		- extensions: dict = None
			- maybe your code is tight
		"""
		
		
		mediaList = []

		if captionList and imageList:
			for image, caption in zip(imageList, captionList):
				mediaList.append([100, self.upload_media(image).mediaValue, caption])
		else:
			if imageList is not None:
				for image in imageList:
					mediaList.append([100, self.upload_media(image).mediaValue, None])
		
		data = {
			"address": None,
			"content": content,
			"title": title,
			"mediaList": mediaList,
			"extensions": extensions,
			"latitude": 0,
			"longitude": 0,
			"eventSource": "GlobalComposeMenu",
		}

		if fansOnly:
			data["extensions"] = {"fansOnly": fansOnly}
		if backgroundColor:
			data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if categoriesList:
			data["taggedBlogCategoryIdList"] = categoriesList
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/blog", data).json()


	def post_wiki(self, title: str, content: str, icon: str | None = None, imageList: list | None = None, keywords: str | None = None, backgroundColor: str | None = None, props: list | None = None, backgroundMediaList: list | None = None, comId: str | int | None = None):
		"""
		Posting wiki.

		**Parameters**:
		- title: str
		- content: str
		- icon: str
		- imageList: list = None
		- keywords: str = None
		- backgroundColor: str = None
			- should be only hex code, like "#000000"
			- if None, it will be just white
		- backgroundMediaList: list
		- props: list
		- fansOnly: bool = False
			- is it for your onlyfans or no?
			- works only if you have fanclub
		"""
		
		data = {
			"label": title,
			"content": content,
			"mediaList": imageList if imageList else [],
			"eventSource": "GlobalComposeMenu",
			"extensions": {},
		}
		if icon:
			data["icon"] = icon
		if keywords:
			data["keywords"] = keywords
		if props:
			data["extensions"].update({"props": props})
		if backgroundMediaList:
			data["extensions"].update({"style": {"backgroundMediaList": backgroundMediaList}})
		if backgroundColor:
			data["extensions"].update({"style": {"backgroundColor": backgroundColor}})

		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/item", data).json()


	def edit_blog(self, blogId: str, title: str | None = None, content: str | None = None, imageList: list | None = None, categoriesList: list | None = None, backgroundColor: str | None = None, fansOnly: bool = False, comId: str | int | None = None):
		"""
		Editing blog.

		**Parameters**:
		- blogId: str
		- title: str = None
		- content: str = None
		- imageList: list = None
		- categoriesList: list = True
		- backgroundColor: str = None
			- should be only hex code, like "#000000"
			- if None, it will be just white
		- fansOnly: bool = False
			- is it for your onlyfans or no?
			- works only if you have fanclub
		"""

		mediaList = []
		if imageList:
			for image in imageList:
				mediaList.append([100, self.upload_media(image).mediaValue, None])

		data = {
			"address": None,
			"mediaList": mediaList,
			"latitude": 0,
			"longitude": 0,
			"eventSource": "PostDetailView",
		}

		if title: data["title"] = title
		if content: data["content"] = content
		if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
		if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if categoriesList: data["taggedBlogCategoryIdList"] = categoriesList
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/blog/{blogId}", data).json()

	def delete_blog(self, blogId: str, comId: str | int | None = None):
		"""
		Deleting blog.

		**Parameters**:
		- blogId: str
		"""
		return self.req.make_sync_request("DELETE", f"/x{comId or self.comId}/s/blog/{blogId}").json()

	def delete_wiki(self, wikiId: str, comId: str | int | None = None):
		"""
		Deleting wiki.

		**Parameters**:
		- wikiId: str
		"""
		return self.req.make_sync_request("DELETE", f"/x{comId or self.comId}/s/item/{wikiId}").json()

	def repost_blog(self, content: str | None = None, blogId: str | None = None, wikiId: str | None = None, comId: str | int | None = None):
		"""
		Reposing blog.

		**Parameters**
		- blogId: str = None
		- wikiId: str = None
			- can be only blogId or wikiId
			- blogId > wikiId
			- if both are None, it will raise Exception
		- content: str = None
		"""
		if blogId is None and wikiId is None: raise SpecifyType
		data = {
			"content": content,
			"refObjectId": blogId if blogId else wikiId,
			"refObjectType": 1 if blogId else 2,
			"type": 2,
		}

		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/blog", data).json()


	def vote_poll(self, blogId: str, optionId: str, comId: str | int | None = None):
		"""
		vote in the poll

		**Parameters**
		- optionId : ID of the poll option
		- blogId : ID of the Blog.
		"""

		data = {
			"value": 1,
			"eventSource": "PostDetailView"
		}
		return self.req.make_sync_request("POST",  f"x{self.comId}/s/blog/{blogId}/poll/option/{optionId}/vote", data).json()


	def like_blog(self, blogId: str | list | None = None, wikiId: str | None = None, comId: str | int | None = None):
		"""
		Like a Blog, Multiple Blogs or a Wiki.

		**Parameters**
		- blogId : ID of the Blog or List of IDs of the Blogs. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
		data: dict = {"value": 4}
		if blogId:
			if isinstance(blogId, str):
				data["eventSource"] = "UserProfileView"
				url = f"/x{comId or self.comId}/s/blog/{blogId}/vote?cv=1.2"
			elif isinstance(blogId, list):
				data["targetIdList"] = blogId
				url = f"/x{comId or self.comId}/s/feed/vote"
			else: raise WrongType(f"blogId: {type(blogId)}")

		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/x{self. comId}/s/item/{wikiId}/vote?cv=1.2"

		else: raise SpecifyType

		return self.req.make_sync_request("POST",  url, data).json()

	def unlike_blog(self, blogId: str | None = None, wikiId: str | None = None, comId: str | int | None = None):
		"""
		Remove a like from a Blog or Wiki.

		**Parameters**
		- blogId : ID of the Blog. (for Blogs)
		- wikiId : ID of the Wiki. (for Wikis)
		"""
		if blogId: url = f"/x{comId or self.comId}/s/blog/{blogId}/vote?eventSource=UserProfileView"
		elif wikiId: url = f"/x{comId or self.comId}/s/item/{wikiId}/vote?eventSource=PostDetailView"
		else: raise SpecifyType

		return self.req.make_sync_request("DELETE",  url).json()


	def play_quiz_raw(self, quizId: str, quizAnswerList: list, quizMode: int = args.QuizMode.NormalMode, comId: str | int | None = None):
		"""
		Send quiz results.

		**Parameters**
		- quizId:  id of quiz
		- quizAnswerList: answer list
		- quizMode: quiz mode
			- hellMode: 1
			- default: 0
		"""
		data = {
			"mode": quizMode,
			"quizAnswerList": quizAnswerList
		}

		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/blog/{quizId}/quiz/result", data).json()

	def play_quiz(self, quizId: str, questionIdsList: list, answerIdsList: list, quizMode: int = args.QuizMode.NormalMode, comId: str | int | None = None):
		"""
		Send quiz results.

		**Parameters**
		- quizId:  id of quiz
		- quizAnswerList: answer list
		- quizMode: quiz mode
			- hellMode: 1
			- default: 0
		"""
		data = {
			"mode": quizMode,
			"quizAnswerList": list()
		}
		for question, answer in zip(questionIdsList, answerIdsList):
			data["quizAnswerList"].append({
				"optIdList": [answer],
				"quizQuestionId": question,
				"timeSpent": 0.0
			})
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/blog/{quizId}/quiz/result", data).json()


	def get_user_blogs(self, userId: str, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Get info about user's blogs.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/blog?type=user&q={userId}&start={start}&size={size}").json()["blogList"]

	def get_user_wikis(self, userId: str, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Get info about user's wikis.

		**Parameters**
		- userId : ID of the User.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/item?type=user-all&start={start}&size={size}&cv=1.2&uid={userId}").json()["itemList"]



	def get_saved_blogs(self, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Recieve all your saved blogs.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/bookmark?start={start}&size={size}").json()["bookmarkList"]



	def get_wiki_info(self, wikiId: str, comId: str | int | None = None):
		"""
		Get all things about wiki post.

		**Parameters**
		- wikiId: wiki id
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/item/{wikiId}").json()

	def get_recent_wiki_items(self, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Get all recent wiki items.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/item?type=catalog-all&start={start}&size={size}").json()["itemList"]

	def get_wiki_categories(self, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Get all wiki categories.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/item-category?start={start}&size={size}").json()["itemCategoryList"]

	def get_wiki_category(self, categoryId: str, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Get all wiki from category.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		- categoryId : wiki category Id
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/item-category/{categoryId}?pagingType=t&start={start}&size={size}").json()

	def get_tipped_users(self, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None, chatId: str | None = None, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Get all users who tipped on your posting.

		**Parameters**
		- blogId: blog Id
		- wikiId: wiki Id
		- quizId: quiz Id
		- fileId: file Id
		- chatId: chat Id
			- can be only one field
		- start : Where to start the list.
		- size : Size of the list.
		"""
		object_types = {
			'blogId': {'id': blogId or quizId, 'url': f"/x{comId or self.comId}/s/blog/{blogId or quizId}/tipping/tipped-users-summary"},
			'wikiId': {'id': wikiId, 'url': f"/x{comId or self.comId}/s/item/{wikiId}/tipping/tipped-users-summary"},
			'chatId': {'id': chatId, 'url': f"/x{comId or self.comId}/s/chat/thread/{chatId}/tipping/tipped-users-summary"},
			'fileId': {'id': fileId, 'url': f"/x{comId or self.comId}/s/shared-folder/files/{fileId}/tipping/tipped-users-summary"}
		}
		for key, value in object_types.items():
			if value['id']:return self.req.make_sync_request("GET", f"{value['url']}?start={start}&size={size}").json()
		else:raise SpecifyType


	def get_blog_info(self, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None, comId: str | int | None = None):
		"""
		Get all info about posting.

		**Parameters**
		- blogId: blog id
		- wikiId: wiki id
		- quizId: quiz id
		- fileId: file id
			- can be only one field
		"""
		if blogId or quizId:
			return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/blog/{blogId or quizId}").json()
		elif wikiId:
			return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/item/{wikiId}").json()
		elif fileId:
			return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/shared-folder/files/{fileId}").json()["file"]
		raise SpecifyType



	def get_blog_comments(self, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None, sorting: str = args.Sorting.Newest, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Get all blog comments.

		**Parameters**
		- blogId: blog id
		- wikiId: wiki id
		- quizId: quiz id
		- fileId: file id
			- can be only one field
		- start : Where to start the list.
		- size : Size of the list.
		- sorting : sorting comments (use ``amino.arguments.Sorting. some``)
		"""
		if sorting not in args.Sorting.all:raise ValueError(f"Sorting.all: {sorting} not in {args.Sorting.all}")
		object_types = {
			'blogId': {'id': blogId or quizId, 'url': f"/x{comId or self.comId}/s/blog/{blogId or quizId}/comment"},
			'wikiId': {'id': wikiId, 'url': f"/x{comId or self.comId}/s/item/{wikiId}/comment"},
			'fileId': {'id': fileId, 'url': f"/x{comId or self.comId}/s/shared-folder/files/{fileId}/comment"}
		}

		for key, value in object_types.items():
			if value['id']:
				return self.req.make_sync_request("GET", f"{value['url']}?sort={sorting}&start={start}&size={size}").json()["commentList"]
		else:
			raise SpecifyType


	def get_blog_categories(self, size: int = 25, comId: str | int | None = None):
		"""
		Get all possible blog categories.

		**Parameters**
		- size: how much you want to get
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/blog-category?size={size}").json()["blogCategoryList"]

	def get_blogs_by_category(self, categoryId: str,start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Get all possible blogs in category.

		**Parameters**:
		- categoryId: category Id
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/blog-category/{categoryId}/blog-list?start={start}&size={size}").json()["blogList"]

	def get_quiz_rankings(self, quizId: str, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Get quiz winners.

		**Parameters**:
		- quizId: quiz Id
		- start : Where to start the list.
		- size : Size of the list.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/blog/{quizId}/quiz/result?start={start}&size={size}").json()



	def get_recent_blogs(self, pageToken: str | None = None, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Get recent blogs.

		**Parameters**
		- size : Size of the list.
		- start : start pos
		- pageToken : Next Page Token.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/feed/blog-all?pagingType=t&size={size}{f'&pageToken={pageToken}' if pageToken else  f'&start={start}'}").json()


	def get_shared_folder_info(self, comId: str | int | None = None):
		"""
		Getting all available info about shared folder.
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/shared-folder/stats").json()["stats"]

	def get_shared_folder_files(self, type: str = args.Sorting2.Latest, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Getting all available files in shared folder.

		**Parameters**
		- type: str = "latest"
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/shared-folder/files?type={type}&start={start}&size={size}").json()["fileList"]
