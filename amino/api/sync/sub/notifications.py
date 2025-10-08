from amino.api.base import BaseClass
from amino import args

class CommunityNotificationsModule(BaseClass):
	comId: str | int | None

	
	def check_notifications(self, comId: str | int | None = None):
		"""
		Checking notifications as read.
		"""
		return self.req.make_sync_request("POST",  f"/x{comId or self.comId}/s/notification/checked").json()

	def delete_notification(self, notificationId: str, comId: str | int | None = None):
		"""
		Delete notification.

		**Parameters**:
		- notificationId: id of the notification
		"""
		return self.req.make_sync_request("DELETE",  f"/x{comId or self.comId}/s/notification/{notificationId}").json()

	def clear_notifications(self, comId: str | int | None = None):
		"""
		Remove all notifications.
		"""
		return self.req.make_sync_request("DELETE",  f"/x{comId or self.comId}/s/notification").json()
	

	def get_notifications(self, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Getting notifications in community.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/notification?pagingType=t&start={start}&size={size}").json()["notificationList"]

	def get_notices(self, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Getting notices in community.

		Notices are NOT notifications. Its like "you are in read only mode", "you got strike", "you got warning", "somebody wants to promote you to curator/leader/curator".

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.make_sync_request("GET", f"/x{comId or self.comId}/s/notice?type=usersV2&status=1&start={start}&size={size}").json()["noticeList"]


	def promotion(self, noticeId: str, type: str = args.PromotionTypes.Accept, comId: str | int | None = None):
		"""
		Accept or deny promotion to curator/leader/agent.

		**Parameters**:
		- noticeId
			- get from `get_notices`
		- type: accept or deny
		"""
		return self.req.make_sync_request("POST", f"/x{comId or self.comId}/s/notice/{noticeId}/{type}").json()
