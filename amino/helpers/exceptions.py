from json.decoder import JSONDecodeError
from json import loads

class UnknownError(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class InvalidSessionType(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class InvalidFunctionСall(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class SocketNotStarted(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)


class IncorrectType(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class AgeTooLow(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class NoCommunity(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)



errors = {
}

def check_exceptions(data):
	try:
		data = loads(data)
		try:code = data["api:statuscode"]
		except:raise UnknownError(data)
	except JSONDecodeError:code = 403
	if code in errors:raise errors[code](data)
	else:raise UnknownError(data)