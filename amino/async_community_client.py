from .objects.auth_data import auth_data
from .helpers.requests_builder import AsyncRequestsBuilder
from .helpers.generator import timezone

from .objects.reqObjects import DynamicObject


class AsyncCommunityClient:
	req: AsyncRequestsBuilder
	comId: str
	
	def __init__(self, profile: auth_data, comId: int, proxies: dict = None):
		self.req = AsyncRequestsBuilder(proxies=proxies, profile=profile)
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



	async def check_in(self, tz: int = None) -> DynamicObject:
		return await self.req.request("POST", f"/x{self.comId}/s/check-in", { "timezone": tz if tz else timezone()})