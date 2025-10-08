
from typing import Optional
from .base_object import BaseObject

class UserProfile(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)
        data = data or {}
        if data.get("userProfile") is not None: data=data.get("userProfile", {})
        
        self.status = data.get("status")
        self.mood_sticker = data.get("moodSticker")
        self.items_count = data.get("itemsCount")
        self.consecutive_check_in_days = data.get("consecutiveCheckInDays")
        self.userId = data.get("uid")
        self.modified_time = data.get("modifiedTime")
        self.following_status = data.get("followingStatus")
        self.online_status = data.get("onlineStatus")
        self.account_membership_status = data.get("accountMembershipStatus")
        self.is_global = data.get("isGlobal")
        self.reputation = data.get("reputation")
        self.posts_count = data.get("postsCount")
        self.members_count = data.get("membersCount")
        self.nickname  = data.get("nickname")
        self.media_list = data.get("mediaList")
        self.icon = data.get("icon")
        self.is_nickname_verified = data.get("isNicknameVerified")
        self.mood = data.get("mood")
        self.level = data.get("level")
        self.notification_subscription_status = data.get("notificationSubscriptionStatus")
        self.push_enabled = data.get("pushEnabled")
        self.membership_status = data.get("membershipStatus")
        self.content = data.get("content")
        self.joined_count = data.get("joinedCount")
        self.role = data.get("role")
        self.comments_count = data.get("commentsCount")
        self.amino_id = data.get("aminoId", "")
        self.comId = data.get("ndcId")
        self.created_time = data.get("createdTime")
        self.extensions = data.get("extensions")
        self.stories_count = data.get("storiesCount")
        self.blogs_count = data.get("blogsCount")
