from .objects.auth_data import auth_data
from .helpers.requests_builder import requestsBuilder
from .helpers.generator import timezone


class CommunityClient:
	req: requestsBuilder
	comId: str
	
	def __init__(self, profile: auth_data, comId: int, verify = None, proxies: dict = None):
		self.req = requestsBuilder(verify=verify, proxies=proxies, profile=profile)
		self.comId = comId


	@property
	def profile(self):
		return self.req.profile
	
	@property
	def userId(self):
		return self.req.profile.uid

	@property
	def sid(self):
		return self.req.profile.sid

	@property
	def deviceId(self):
		return self.req.profile.deviceId



	def check_in(self, tz: int = None) -> dict:
		result = self.req.request("POST", f"/x{self.comId}/s/check-in", { "timezone": tz if tz else timezone()})
		self.req.profile.sid, self.req.profile.uid = None, None
		return result