def set_attributes(instance, _ListObjects):
	if _ListObjects:
		attributes = tuple(attr for attr in dir(_ListObjects[0]) if not attr.startswith("__") and not callable(getattr(_ListObjects[0], attr)) and attr != _ListObjects[0].__class__.__name__)
		for attr in attributes:
			setattr(instance, attr, tuple(getattr(user, attr, None) for user in _ListObjects))
