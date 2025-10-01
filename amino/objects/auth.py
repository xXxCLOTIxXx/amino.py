from . import UserProfile, Account
from .base_object import BaseObject

class AuthData(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)

        self.uid: str | None = data.get("auid")
        self.sid:  str | None= data.get("sid")
        self.user_profile:  UserProfile = UserProfile(data)
        self.account:  Account = Account(data)