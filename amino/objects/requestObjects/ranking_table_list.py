class RankingTableList:
	__slots__ = ("data", "title", "level", "reputation", "id")
	def __init__(self, data: list[dict]):
		if not data:
			for attr in self.__slots__:
				setattr(self, attr, None)

			return
		self.data = data
		self.title = tuple(x.get("title") for x in data)
		self.level = tuple(x.get("level") for x in data)
		self.reputation = tuple(x.get("reputation") for x in data)
		self.id = tuple(x.get("id") for x in data)