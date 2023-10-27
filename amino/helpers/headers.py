from .generators import generate_deviceId, signature

def headers(data = None, content_type = None, sid: str = None, deviceId: str = None, user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2"):
	headers = {
		"NDCDEVICEID": deviceId if deviceId else self.generate_deviceId(),
		"NDCLANG": "ru",
		"Accept-Language": "ru-RU",
		"SMDEVICEID": "20230109055041eecd2b9dd8439235afe4522cb5dacd26011dba6bbfeeb752", 
		"User-Agent": user_agent,
		"Content-Type": "application/json; charset=utf-8",
		"Host": "service.narvii.com",
		"Accept-Encoding": "gzip",
		"Connection": "Upgrade"
		}
	if data:
		headers["Content-Length"] = str(len(data))
		headers["NDC-MSG-SIG"] = signature(data=data)
	if sid:headers["NDCAUTH"] = f"sid={sid}"
	if content_type:headers["Content-Type"] = content_type
	return headers

def ws_headers(final: str, sid: str = None, deviceId: str = None):
	return {
			"NDCDEVICEID": deviceId if deviceId else generate_deviceId(),
			"NDCAUTH": f"sid={sid}",
			"NDC-MSG-SIG": signature(final)
		}
