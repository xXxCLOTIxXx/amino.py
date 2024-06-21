from ..reqObjects import DynamicObject

class Event:
	"""
		class with data about a new event
		
	"""
	__slots__ = (
		"data", "comId", "alertOption", "membershipStatus",
		"actions", "target", "params", "threadType", "duration",
		"id", "message"
	)

	def __init__(self, data: dict):
		self.data = data
		params = data.get("params", {})
		
		self.comId = data.get("ndcId")
		self.alertOption = data.get("alertOption")
		self.membershipStatus = data.get("membershipStatus")
		self.actions = data.get("actions")
		self.target = data.get("target")
		self.params = params
		self.threadType = params.get("threadType")
		self.duration = params.get("duration")
		self.id = data.get("id")
		self.message = DynamicObject(data.get("chatMessage", {}))