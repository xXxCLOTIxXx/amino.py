from .client import Client
from .community_client import CommunityClient
from .helpers import generators, exceptions
from . import asynclib
from . import models
from .helpers.types import all_ws_types


from os import system as s
from json import loads
from requests import get


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



__title__ = 'amino.api'
__author__ = 'Xsarz'
__license__ = 'MIT'
__copyright__ = 'Copyright 2023-2024 Xsarz'
__version__ = '0.2.5.6'
try:__newest__ = loads(get("https://pypi.org/pypi/amino.api/json").text)["info"]["version"]
except:__newest__ = __version__


def check_version() -> tuple:
	return (False if __version__ != __newest__ else True, __newest__) 


def library_update():
	version = check_version()
	if version[0] is False:
		s(f"pip install -U {__title__}=={version[1]}.")
		return f"Library updated successfully {__version__} -> {version[1]}."
	return f"The latest version is already installed -> {__version__}."


if __version__[-1] != "b":
	if check_version()[0] is False:
		s('cls || clear')
		print(f'\033[38;5;214m{__title__} made by {__author__}\nPlease update the library. Your version: {__version__}  A new version: {__newest__}\033[0m')
		update = input("\033[38;5;214mDo you want to update library now? (y/n) >>\033[0m ")
		if update.lower() == 'y':print(library_update())