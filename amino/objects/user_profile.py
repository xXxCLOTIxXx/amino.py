
from typing import Optional
from .base_object import BaseObject

class UserProfile(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)

        data = data.get("userProfile", {})
        self.data = data

        self.status: int = data.get("status", 0)
        self.mood_sticker: Optional[str] = data.get("moodSticker")
        self.items_count: int = data.get("itemsCount", 0)
        self.consecutive_check_in_days: Optional[str] = data.get("consecutiveCheckInDays")
        self.uid: str = data.get("uid", "")
        self.modified_time: str = data.get("modifiedTime", "")
        self.following_status: int = data.get("followingStatus", 0)
        self.online_status: int = data.get("onlineStatus", 0)
        self.account_membership_status: int = data.get("accountMembershipStatus", 0)
        self.is_global: bool = data.get("isGlobal", False)
        self.reputation: int = data.get("reputation", 0)
        self.posts_count: int = data.get("postsCount", 0)
        self.members_count: int = data.get("membersCount", 0)
        self.nickname: str = data.get("nickname", "")
        self.media_list: Optional[str] = data.get("mediaList")
        self.icon: str = data.get("icon", "")
        self.is_nickname_verified: bool = data.get("isNicknameVerified", False)
        self.mood: Optional[str] = data.get("mood")
        self.level: int = data.get("level", 0)
        self.notification_subscription_status: int = data.get("notificationSubscriptionStatus", 0)
        self.push_enabled: bool = data.get("pushEnabled", False)
        self.membership_status: int = data.get("membershipStatus", 0)
        self.content: Optional[str] = data.get("content")
        self.joined_count: int = data.get("joinedCount", 0)
        self.role: int = data.get("role", 0)
        self.comments_count: int = data.get("commentsCount", 0)
        self.amino_id: str = data.get("aminoId", "")
        self.ndc_id: int = data.get("ndcId", 0)
        self.created_time: str = data.get("createdTime", "")
        self.extensions: Optional[str] = data.get("extensions")
        self.stories_count: int = data.get("storiesCount", 0)
        self.blogs_count: int = data.get("blogsCount", 0)
