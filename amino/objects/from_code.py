from .base_object import BaseObject


class FromCode(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)
        data = data.get("linkInfoV2", {})

        extensions: dict = data.get("extensions", {})
        link_info: dict = extensions.get("linkInfo", {})
        community_info: dict = extensions.get("community", {})

        self.path = data.get("path")
        self.objectType = link_info.get("objectType")
        self.shortCode = link_info.get("shortCode")
        self.fullPath = link_info.get("fullPath")
        self.targetCode = link_info.get("targetCode")
        self.objectId = link_info.get("objectId")
        self.shortUrl = link_info.get("shareURLShortCode")
        self.fullUrl = link_info.get("shareURLFullPath")
        self.comIdPost = link_info.get("ndcId")
        self.comId = self.comIdPost or community_info.get("ndcId")


class LinkIdentify(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)

        self.community: dict = data.get("community", {})
        self.path: str = data.get("path", "")
        self.isCurrentUserJoined: bool = data.get("isCurrentUserJoined", False)
        self.invitationId: str = data.get("invitationId", "")