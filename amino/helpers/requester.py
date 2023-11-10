from typing import Union
from aiohttp import ClientSession
from requests import Session
from .exceptions import check_exceptions
from datetime import datetime

#thanks to August for help with the fix "Max retries exceeded with url" (http_connect add)
#Telegram: @augustlight





class Requester:
	api = "https://service.aminoapps.com/api/v1"

	def __init__(self, session: Session, proxies: dict = None, verify = None, http_connect: bool = False, requests_debug: bool = False):
		self.session = session
		self.proxies = proxies
		self.verify = verify
		self.http_connect=http_connect
		self.requests_debug = requests_debug
		if http_connect is True:
			self.api = "http://service.aminoapps.com:80/api/v1"
			self.verify = False
			self.session.verify = self.verify
		
		self.request_log(title="request api",type="http" if http_connect else "https", message=f"Api url: {self.api}")

		



	def make_request(self, method: str, endpoint: str, data = None, successfully: int = 200, headers = None, timeout=None):
		self.request_log(type=method, message=f"Sending a request on endpoint: {endpoint}")
		response = self.session.request(method, f"{self.api}{endpoint}", proxies=self.proxies, verify=self.verify, data=data, headers=headers, timeout=timeout)
		if successfully: return check_exceptions(response.text, response.status_code) if response.status_code != successfully else response
		return response

	
	def request_log(self, type: str, message: str, title: str = "request"):
		if self.requests_debug:print(f"[{datetime.now()}][{title}][{type}]: {message}")




class AsyncRequester:
	api = "https://service.aminoapps.com/api/v1"

	def __init__(self, session: ClientSession, proxies: dict = None, verify = None, http_connect: bool = False, requests_debug: bool = False):
		self.session = session
		self.proxies = proxies
		self.verify = verify
		self.http_connect=http_connect
		self.requests_debug=requests_debug
		if http_connect is True:
			self.api = "http://service.aminoapps.com:80/api/v1"
			self.verify = False
			self.session.verify = self.verify
		self.request_log(title="request api",type="http" if http_connect else "https", message=f"Api url: {self.api}")


	async def make_request(self, method: str, endpoint: str, data = None, successfully: int = 200, headers = None, timeout=None):
		self.request_log(type=method, message=f"Sending a request on endpoint: {endpoint}")
		response = await self.session.request(method, f"{self.api}{endpoint}", data=data, headers=headers, timeout=timeout)
		if successfully: return check_exceptions(await response.text(), response.status) if response.status != successfully else response
		return response

	def request_log(self, type: str, message: str, title: str = "request"):
		if self.requests_debug:print(f"[{datetime.now()}][{title}][{type}]: {message}")