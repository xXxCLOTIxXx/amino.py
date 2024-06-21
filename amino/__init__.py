"""
Library for working with amino servers [https://aminoapps.com/]

Has both synchronous and asynchronous versions

Note: the library is in testing, so an asynchronous version will be added as soon as testing of all functions is completed
"""

from .client import Client
from .community_client import CommunityClient
from .async_client import AsyncClient
from .async_community_client import AsyncCommunityClient

from .helpers.exceptions import *
from .helpers.generator import (
    generate_deviceId, generate_user_agent, signature,
    sid_created_time, sid_to_ip_address, sid_to_client_type, sid_to_uid,
    decode_sid
)

from .objects import reqObjects as objects
from .objects import args as arguments

__title__ = 'amino.api'
__author__ = 'Xsarz'
__license__ = 'MIT'
__copyright__ = 'Copyright 2024 Xsarz'
__version__ = '0.4.7'

"""
TODO:
 add response objects
 add async version
 rewrite some functions
"""