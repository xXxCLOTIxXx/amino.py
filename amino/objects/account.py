from typing import Optional, Dict, Any
from .base_object import BaseObject


class Account(BaseObject):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        data = data.get("account", {})
        self.data = data

        self.username: Optional[str] = data.get("username")
        self.status: int = data.get("status", 0)
        self.userId: str = data.get("uid", "")
        self.modified_time: str = data.get("modifiedTime", "")
        self.twitter_id: Optional[str] = data.get("twitterID")
        self.activation: int = data.get("activation", 0)
        self.phone_number_activation: int = data.get("phoneNumberActivation", 0)
        self.email_activation: int = data.get("emailActivation", 0)
        self.apple_id: Optional[str] = data.get("appleID")
        self.facebook_id: Optional[str] = data.get("facebookID")
        self.nickname: str = data.get("nickname", "")
        self.media_list: Optional[str] = data.get("mediaList")
        self.google_id: Optional[str] = data.get("googleID")
        self.icon: str = data.get("icon", "")
        self.security_level: int = data.get("securityLevel", 0)
        self.phone_number: Optional[str] = data.get("phoneNumber")
        self.membership: Optional[str] = data.get("membership")
        self.advanced_settings: Dict[str, Any] = data.get("advancedSettings", {})
        self.role: int = data.get("role", 0)
        self.aminoId_editable: bool = data.get("aminoIdEditable", False)
        self.aminoId: str = data.get("aminoId", "")
        self.created_time: str = data.get("createdTime", "")
        self.extensions: Dict[str, Any] = data.get("extensions", {})
        self.email: str = data.get("email", "")