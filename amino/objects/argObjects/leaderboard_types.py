class LeaderboardTypes:
	"""
	leaderboard types

	attributes:
	
	- Day
	- Week
	- Reputation
	- Check
	- Quiz

	- all (list of all attributes)

	"""
	
	Day: int = 1
	Week: int = 2
	Reputation: int = 3
	Check: int = 4
	Quiz: int = 5
	
	all: tuple = (Day, Week, Reputation, Check, Quiz)
