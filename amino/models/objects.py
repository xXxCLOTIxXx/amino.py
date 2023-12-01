from ..helpers.types import renamed
from json import loads

class ObjectCreator:
	def __init__(self, data = {}):
		self.json = self.add_standard_keys(data)

	@property
	def get_value(self):
		return self.json

	@property
	def get_value_type(self):
		return type(self.json)

	def get(self, key, default = None):
		if isinstance(self.json, dict):return self.json.get(key, default)
		raise Exception("Object is not a dictionary.")


	def add_standard_keys(self, data: dict):
		if isinstance(data, dict):
			for i in renamed.keys():
				if i in data.keys():
					data[renamed.get(i)] = data.get(i, {})
					if ':' in i:del data[i]
			return data
		return data


	def class_wrapper(self, data):
		if isinstance(data, dict):
			return self.__class__(self.add_standard_keys(data))
		if isinstance(data, list):
			temp = list()
			for i in data:
				temp.append(self.class_wrapper(i))
			return temp
		if isinstance(data, str):
			try:
				data = loads(data)
				return self.__class__(self.add_standard_keys(data))
			except:
				return data

		return data


	def __getattr__(self, item: str):
		return self.class_wrapper(self.json.get(item, {}))

	def __repr__(self):
		return repr(self.json)


class AsyncObjectCreator(ObjectCreator):
	pass