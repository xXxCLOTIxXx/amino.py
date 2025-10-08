from . import Message

class Event:
	"""
		class with data about a new event
	"""

	def __init__(self, data: dict):
		self.data = data or {}
		params = data.get("params", {})
		self.message: Message = Message(data.get("chatMessage", {}))
		
		self.comId = data.get("ndcId")
		self.alertOption = data.get("alertOption")
		self.membershipStatus = data.get("membershipStatus")
		self.actions = data.get("actions")
		self.target = data.get("target")
		self.params = params
		self.threadType = params.get("threadType")
		self.duration = params.get("duration")
		self.id = data.get("id")