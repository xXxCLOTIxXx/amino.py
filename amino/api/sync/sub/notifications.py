from amino.api.base import BaseClass
from amino import args

class CommunityNotificationsModule(BaseClass):
	comId: str | None

	
	def check_notifications(self):
		"""
		Checking notifications as read.
		"""
		return self.req.make_sync_request("POST",  f"/x{self.comId}/s/notification/checked").json()

	def delete_notification(self, notificationId: str):
		"""
		Delete notification.

		**Parameters**:
		- notificationId: id of the notification
		"""
		return self.req.make_sync_request("DELETE",  f"/x{self.comId}/s/notification/{notificationId}").json()

	def clear_notifications(self):
		"""
		Remove all notifications.
		"""
		return self.req.make_sync_request("DELETE",  f"/x{self.comId}/s/notification").json()
	

	def get_notifications(self, start: int = 0, size: int = 25):
		"""
		Getting notifications in community.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.make_sync_request("GET", f"/x{self.comId}/s/notification?pagingType=t&start={start}&size={size}").json()["notificationList"]

	def get_notices(self, start: int = 0, size: int = 25):
		"""
		Getting notices in community.

		Notices are NOT notifications. Its like "you are in read only mode", "you got strike", "you got warning", "somebody wants to promote you to curator/leader/curator".

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return self.req.make_sync_request("GET", f"/x{self.comId}/s/notice?type=usersV2&status=1&start={start}&size={size}").json()["noticeList"]


	def promotion(self, noticeId: str, type: str = args.PromotionTypes.Accept):
		"""
		Accept or deny promotion to curator/leader/agent.

		**Parameters**:
		- noticeId
			- get from `get_notices`
		- type: accept or deny
		"""
		return self.req.make_sync_request("POST", f"/x{self.comId}/s/notice/{noticeId}/{type}").json()
