from .base_object import BaseObject
from .user_profile import UserProfile

class Comment:
    def __init__(self, data: dict):
        self.votesSum = data.get("votesSum")
        self.votedValue = data.get("votedValue")
        self.mediaList = data.get("mediaList")
        self.parentComId = data.get("parentNdcId")
        self.parentId = data.get("parentId")
        self.parentType = data.get("parentType")
        self.content = data.get("content")
        self.extensions = data.get("extensions")
        self.comId = data.get("ndcId")
        self.modifiedTime = data.get("modifiedTime")
        self.createdTime = data.get("createdTime")
        self.commentId = data.get("commentId")
        self.subcommentsCount = data.get("subcommentsCount")
        self.type = data.get("type")

        self.author = UserProfile(data.get("author", {}))
