
from .community_client import CommunityClient
from .client import Client

def create_community_client(client: Client, comId: int = None, community_link: str = None, aminoId: str = None):
	return CommunityClient(
		comId=comId,
		community_link=community_link,
		aminoId=aminoId,
		profile=client.profile,
		language=client.language,
		user_agent=client.user_agent,
		auto_user_agent=client.auto_user_agent,
		deviceId=client.deviceId,
		auto_device=client.auto_device,
		proxies=client.proxies,
		certificate_path=client.verify,
		http_connect=client.http_connect,
		requests_debug=client.requests_debug
	)
