from json.decoder import JSONDecodeError
from json import loads

class UnknownError(Exception):
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

class SpecifyType(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class WrongType(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class UnsupportedLanguage(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)


class ServiceUnavailable(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)



errors = {
	"s503": ServiceUnavailable
}

def check_exceptions(data, status):
	try:
		data = loads(data)
		try:code = data["api:statuscode"]
		except:raise UnknownError(data)
	except JSONDecodeError:
		if status == 503:code="s503"
		else:code="s403"
	if code in errors:raise errors[code](data)
	else:raise UnknownError(data)