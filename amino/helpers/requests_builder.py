from ..objects.auth_data import auth_data
from ..helpers.generator import signature, generate_deviceId
from ..objects.constants import (
	host, api
)
from .exceptions import check_exceptions

from typing import Union
from requests import Session
from ujson import dumps


class requestsBuilder:
    profile: auth_data
    session: Session = Session()
    proxies: dict
    verify: dict

    def __init__(self, profile: auth_data, verify = None, proxies: dict = None):
        self.profile = profile
        self.proxies = proxies
        self.verify = verify


    def header(self, data: bytes = None, content_type: str = "application/json"):
        headers = {
            "NDCDEVICEID": self.profile.deviceId if self.profile.deviceId else generate_deviceId(),
            "NDCLANG": self.profile.language.lower(),
            "Accept-Language": f"{self.profile.language.lower()}-{self.profile.language.upper()}",
            "User-Agent": self.profile.user_agent,
            "Host": "service.aminoapps.com",
            "Accept-Encoding":  "gzip, deflate",
            "Accept": "*/*",
            "Connection": "keep-alive",
            }
        if data:
            headers["Content-Length"] = str(len(data))
            headers["NDC-MSG-SIG"] = signature(data=data)
            
        if self.profile.sid:headers["NDCAUTH"] = f"sid={self.profile.sid}"
        if self.profile.uid: headers["AUID"] = self.profile.uid
        if content_type: headers["Content-Type"] = content_type
        
        return headers



    def request(self, method: str, endpoint: str, data: Union[str, bytes] = None, successfully: int = 200, timeout=None, base_url: str = api) -> dict:
        if isinstance(data, dict): data = dumps(data)
        if method.lower() == "post":content_type= "application/json" if data is not None else "application/x-www-form-urlencoded"
        else:content_type = None

        resp = self.session.request(method.upper(), f"{base_url}{endpoint}", data=data, headers=self.header(
            data=data, content_type=content_type
        ), timeout=timeout, verify=self.verify, proxies=self.proxies)
        return check_exceptions(resp.text) if resp.status_code != successfully else resp.json()