class VoiceChatJoinPermissions:
	"""
	types of voice chat access

	attributes:
	
	- Open
	- ApprovalRequired
	- InviteOnly
	
	- all (list of all attributes)

	"""
	  
	Open: int = 1
	ApprovalRequired: int = 2
	InviteOnly: int = 3

	all: tuple = (Open, ApprovalRequired, InviteOnly)
