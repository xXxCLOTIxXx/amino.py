from amino.api.base import BaseClass
from amino.helpers.generator import req_time, timezone, sid_to_uid, get_certs
from amino import SpecifyType, WrongType, AuthData, Account, MediaObject, args, BaseObject, UserProfile

from orjson import dumps
from typing import BinaryIO

class AccountModule(BaseClass):
	

	def upload_media(self, file: BinaryIO, fileType: str | None = None) -> MediaObject: ...
	def ws_headers(self, sid: str | None, final: str, deviceId: str | None) -> dict: ...
	def ws_connect(self, headers: dict, final: str) -> None: ...
	def ws_disconnect(self) -> None: ...

	def pub_key(self) -> dict:
		proxies = self.req.dorks_api_proxies if isinstance(self.req.dorks_api_proxies, dict) else None
		data=dumps(get_certs(self.userId, proxies))
		return self.req.make_sync_request("POST", "/g/s/security/public_key", data).json()

	def login(self, email: str, password: str | None = None, secret: str | None = None, client_type: int = args.ClientTypes.User) -> AuthData:
		"""
		Login into an account.

		**Parameters**
		- email : Email of the account.
		- password : Password of the account.
		- secret : secret of the account
		- client_type: Type of Client.
		"""
		if password is None and secret is None: raise SpecifyType("Either password or secret must be provided.")
		result = self.req.make_sync_request("POST", "/g/s/auth/login", {
			"email": email,
			"v": 2,
			"secret": secret if secret else f"0 {password}",
			"deviceID": self.deviceId,
			"clientType": client_type,
			"action": "normal",
		})

		data = result.json()
		self.set_sid(data["sid"])
		self.set_userId(data["auid"])
		self.pub_key()
		if self.socket_enable:
			final = f"{self.deviceId}|{req_time()}"
			self.ws_connect(final=final, headers=self.ws_headers(self.sid, final, self.deviceId))
		self.me = AuthData(data)
		return self.me

	def login_phone(self, phone: str, password: str | None = None, secret: str | None = None, client_type: int = args.ClientTypes.User) -> AuthData:
		"""
		Login into an account.

		**Parameters**
		- phone : phone number of the account.
		- password : Password of the account.
		- client_type: Type of Client.
		"""
		if password is None and secret is None: raise SpecifyType("Either password or secret must be provided.")
		result = self.req.make_sync_request("POST", "/g/s/auth/login", {
			"phoneNumber": phone,
			"v": 2,
			"secret": secret if secret else f"0 {password}",
			"deviceID": self.deviceId,
			"clientType": client_type,
			"action": "normal",
		}).json()
		
		self.set_sid(result["sid"])
		self.set_userId(result["auid"])
		self.pub_key()
		if self.socket_enable:
			final = f"{self.deviceId}|{req_time()}"
			self.ws_connect(final=final, headers=self.ws_headers(self.sid, final, self.deviceId))
		self.me = AuthData(result)
		return self.me

	def login_sid(self, sid: str) -> AuthData:
		"""
		Login into an account.

		**Parameters**
		- sid : auth sid
		"""
		self.set_sid(sid)
		self.set_userId(sid_to_uid(sid))
		self.pub_key()
		if self.socket_enable:
			final = f"{self.deviceId}|{req_time()}"
			self.ws_connect(final=final, headers=self.ws_headers(self.sid, final, self.deviceId))
		self.me = AuthData({"auid": self.userId, "sid": self.sid})
		return self.me

	def logout(self, client_type: int = args.ClientTypes.User) -> BaseObject:
		"""
		Logout from an account.
		"""
		result = self.req.make_sync_request("POST", "/g/s/auth/logout", {
			"deviceID": self.deviceId,
			"clientType": client_type,
		}).json()
		self.set_sid(None)
		self.set_userId(None)
		self.me = AuthData({})
		if self.socket_enable:
			self.ws_disconnect()
		return BaseObject(result)

	def restore_account(self, email: str, password: str) -> BaseObject:
		"""
		Restore a deleted account.

		**Parameters**
		- email : Email of the account.
		- password : Password of the account.
		"""
		return BaseObject(self.req.make_sync_request("POST", "/g/s/account/delete-request/cancel", {
			"secret": f"0 {password}",
			"deviceID": self.deviceId,
			"email": email,
		}).json())

	def verify_account(self, email: str, code: str) -> BaseObject:
		"""
		Verify an account.

		**Parameters**
		- email : Email of the account.
		- code : Verification code.
		"""
		return BaseObject(self.req.make_sync_request("POST", "/g/s/auth/check-security-validation", {
			"validationContext": {
				"type": 1,
				"identity": email,
				"data": {"code": code}},
			"deviceID": self.deviceId,
		}).json())

	def request_verify_code(self, email: str, resetPassword: bool = False) -> BaseObject:
		"""
		Request an verification code to the targeted email.

		**Parameters**
		- email : Email of the account.
		- resetPassword : If the code should be for Password Reset.
		"""

		data = {
			"identity": email,
			"type": 1,
			"deviceID": self.deviceId,
		}
		if resetPassword is True:
			data["level"] = 2
			data["purpose"] = "reset-password"
		return BaseObject(self.req.make_sync_request("POST", "/g/s/auth/request-security-validation", data).json())

	def activate_account(self, email: str, code: str) -> BaseObject:
		"""
		Activate an account.

		**Parameters**
		- email : Email of the account.
		- code : Verification code.
		"""
		
		return BaseObject(self.req.make_sync_request("POST", "/g/s/auth/activate-email", {
			"type": 1,
			"identity": email,
			"data": {"code": code},
			"deviceID": self.deviceId,
		}).json())

	def delete_account(self, password: str) -> BaseObject:
		"""
		Delete an account.

		**Parameters**
		- password: Password of the account.
		"""
		return BaseObject(self.req.make_sync_request("POST", "/g/s/account/delete-request", {
			"deviceID": self.deviceId,
			"secret": f"0 {password}",
		}).json())

	def change_password(self, email: str, password: str, code: str) -> BaseObject:
		"""
		Change password of an account.

		**Parameters**
		- email : Email of the account.
		- code : Verification code.
		- old_password : old password of account.
		- new_password : new password for account.

		"""
		
		return BaseObject(self.req.make_sync_request("POST", "/g/s/auth/reset-password", {
			"updateSecret": f"0 {password}",
			"emailValidationContext": {
				"data": {
					"code": code
				},
				"type": 1,
				"identity": email,
				"level": 2,
				"deviceID": self.deviceId
			},
			"phoneNumberValidationContext": None,
			"deviceID": self.deviceId,
		}).json())

	#worked?
	def change_email(self, password: str, old_email: str, old_code: str, new_email: str, new_code: str) -> BaseObject:
		"""
		Change email of an account.

		**Parameters**
		- password : Password from account.
		- old_email : Old email of the account.
		- old_code : Verification code from old email.
		- new_email : New email for account.
		- new_code : Verification code from new email.
		"""

		data = {
			"secret": f"0 {password}",
			"deviceTokenType": 0,
			"clientType": 100,
			"systemPushEnabled": 1,
			"newValidationContext": {
				"identity": new_email,
				"data": {
					"code": str(new_code)
				},
				"deviceID": self.deviceId,
				"type": 1,
				"level": 1
			},
			"locale": "en_BY",
			"level": 1,
			"oldValidationContext": {
				"identity": old_email,
				"data": {
					"code": str(old_code)
				},
				"deviceID": self.deviceId,
				"type": 1,
				"level": 1
			},
			"bundleID": "com.narvii.master",
			"timezone": timezone(),
			"deviceID": self.deviceId,
			"clientCallbackURL": "narviiapp://default"
		}

		return BaseObject(self.req.make_sync_request("POST", f"/g/s/auth/update-email", data).json())

	def check_device(self, deviceId: str, locale: str = "en_US") -> BaseObject:
		"""
		Check if the Device ID is valid.

		**Parameters**
		- deviceId : ID of the Device.
		- locale : Locale like "ru_RU", "en_US"
		"""
		data = {
			"deviceID": deviceId,
			"bundleID": "com.narvii.amino.master",
			"clientType": 100,
			"timezone": timezone(),
			"systemPushEnabled": True,
			"locale": locale,
		}

		return BaseObject(self.req.make_sync_request("POST", f"/g/s/device", data).json())

	def get_eventlog(self) -> BaseObject:
		"""
		Get eventlog
		"""
		return BaseObject(self.req.make_sync_request("GET", f"/g/s/eventlog/profile?language={self.language}").json())

	def get_account_info(self) -> Account:
		"""
		Getting account info about you.
		"""
		return Account(self.req.make_sync_request("GET", "/g/s/account").json())

	def configure_profile(self, age: int, gender: int = args.Gender.non_binary) -> BaseObject:
		"""
		Configure the settings of an account.

		**Parameters**
		- age : Age of the account. Minimum is 13.
		- gender : Gender of the account.
			- ``Gender.male``, ``Gender.female`` or ``Gender.non_binary``
		"""
		if gender not in args.Gender.all:raise SpecifyType
		return BaseObject(self.req.make_sync_request("POST", "/g/s/persona/profile/basic", {
			"age": max(13, age),
			"gender": gender,
		}).json()	)

	def activity_status(self, status: bool) -> BaseObject:
		"""
		Sets your activity status to offline or online.

		**Parameters**
		- status: bool
			- True: online
			- False: offline
		"""

		if status not in (True, False): raise WrongType(status)
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/user-profile/{self.userId}/online-status", {
			"onlineStatus": 1 if status is True else 2,
			"duration": 86400,
		}).json())

	def set_privacy_status(self, isAnonymous: bool | None = False, getNotifications: bool | None = False) -> BaseObject:

		"""
		Edit account's Privacy Status.

		**Parameters**
		- isAnonymous : If visibility should be Anonymous or not.
		- getNotifications : If account should get new Visitors Notifications.
		"""

		data = {}

		if isAnonymous is not None:
			if isAnonymous is False: data["privacyMode"] = 1
			if isAnonymous is True: data["privacyMode"] = 2
		if getNotifications:
			if getNotifications is False: data["notificationStatus"] = 2
			if getNotifications is True: data["privacyMode"] = 1
		if not data:raise SpecifyType("Specify arguments.")

		return BaseObject(self.req.make_sync_request("POST", f"/g/s/account/visit-settings", data).json())

	def set_amino_id(self, aminoId: str) -> BaseObject:
		"""
		Edit account's Amino ID.

		**Parameters**
			- aminoId : Amino ID of the Account.
		"""
		return BaseObject(self.req.make_sync_request("POST", f"/g/s/account/change-amino-id", {"aminoId": aminoId}).json())

	def edit_profile(self, nickname: str | None = None, content: str | None = None, icon: BinaryIO | None = None, backgroundColor: str | None = None, backgroundImage: str | None = None, defaultBubbleId: str | None = None) -> UserProfile:
		"""
		Edit account's Profile.

		**Parameters**
		- nickname : Nickname of the Profile.
		- content : Biography of the Profile.
		- icon : Icon of the Profile.
		- backgroundImage : Url of the Background Picture of the Profile.
		- backgroundColor : Hexadecimal Background Color of the Profile.
		- defaultBubbleId : Chat bubble ID.
		
		"""
		
		data = {
			"address": None,
			"latitude": 0,
			"longitude": 0,
			"mediaList": None,
			"eventSource": "UserProfileView",
		}

		if nickname:
			data["nickname"] = nickname
		if icon:
			data["icon"] = self.upload_media(icon).mediaValue
		if content:
			data["content"] = content
		if backgroundColor:
			data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if backgroundImage:
			data["extensions"] = {"style": {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}}
		if defaultBubbleId:
			data["extensions"] = {"defaultBubbleId": defaultBubbleId}
	
		return UserProfile(self.req.make_sync_request("POST", f"/g/s/user-profile/{self.userId}", data).json())

