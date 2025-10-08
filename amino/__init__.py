from .helpers.exceptions import *
from .objects import args
from .objects import *

from .helpers import log
from .helpers.generator import (
    gen_deviceId, update_deviceId, timers, timezone,
    decode_sid, sid_to_uid, sid_to_ip_address, sid_to_created_time, sid_to_client_type
)


from .helpers import log, logging

from .client import Client
from .sub_client import SubClient

from .helpers.constants import set_dorksapi_key

def set_log_level(level = logging.INFO):
    """
    Sets the logging level.

    :param level: The new logging level (e.g., logging.DEBUG, logging.ERROR).
    """
    log.set_level(level)


def enable_file_logging(log_file: str = 'kyodo.log'):
    """
    Enables logging to a file.

    :param log_file: The file where logs will be written.
    """
    log.enable_file_logging(log_file)


def disable_file_logging():
    """
    Disables logging to a file.
    """
    if log.log_to_file:
        log.log_to_file = False
        log.logger.removeHandler(log.logger.handlers[-1])


__title__ = 'amino.py.api'
__author__ = 'Xsarz'
__license__ = 'MIT'
__copyright__ = f'Copyright 2025-2026 {__author__}'
__version__ = '0.9.8.2hf'
__telegram__ = 'https://t.me/DXsarzHUB'


from requests import get
try:__newest__ = get("https://pypi.org/pypi/amino.py.api/json").json().get("info", {}).get("version", __version__)
except:__newest__=__version__
if __version__ != __newest__:
	log.warning(f'{__title__} made by {__author__} [{__telegram__}].\nPlease update the library. Your version: {__version__}  A new version: {__newest__}')