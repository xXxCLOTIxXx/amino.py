class UsersTypes:
	"""
	user sorting type

	attributes:
	
	- Recent
	- Banned
	- Featured
	- Leaders
	- Curators
	
	- all (list of all attributes)

	"""
	  
	Recent: str = "recent"
	Banned: str = "banned"
	Featured: str = "featured"
	Leaders: str = "leaders"
	Curators: str = "curators"

	all: tuple = (Recent, Banned, Featured, Leaders, Curators)
