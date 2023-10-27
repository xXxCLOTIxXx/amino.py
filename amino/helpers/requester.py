from typing import Union
from aiohttp import ClientSession
from requests import Session


from .exceptions import InvalidFunctionСall, InvalidSessionType
from .exceptions import check_exceptions

class Requester:
	def __init__(self, session: Union[ClientSession, Session], proxies: dict = None, verify = None):
		self.api = "https://service.narvii.com/api/v1"
		self.session = session
		self.proxies = proxies
		self.verify = verify

		if isinstance(self.session, ClientSession):self.session_type = "async"
		elif isinstance(self.session, Session):self.session_type = "sync"
		else:raise InvalidSessionType(type(self.session))


	def make_request(self, method: str, endpoint: str, body = None, successfully: int = 200, headers = None, timeout=None):
		if self.session_type!="sync":raise InvalidFunctionСall("You cannot select this function, your session type is async")
		response = self.session.request(method, f"{self.api}{endpoint}", proxies=self.proxies, verify=self.verify, data=body, headers=headers, timeout=timeout)
		if successfully: return check_exceptions(response.text, response.status_code) if response.status_code != successfully else response
		return response


	async def make_async_request(self, method: str, endpoint: str, body = None, successfully: int = 200, headers = None):
		if self.session_type!="sync":raise InvalidFunctionСall("You cannot select this function, your session type is sync")
		response = await self.session.request(method, f"{self.api}{endpoint}", data=dumps(body) if body else None, headers=headers)
		if successfully: return check_exceptions(await response.text(), response.status) if response.status != successfully else response
		return response