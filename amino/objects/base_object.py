

class BaseObject:
    api_message: str | None
    api_statuscode: str | None
    api_duration: str | None
    api_timestamp: str | None
    data: dict

    def __init__(self, data: dict):
        self.data = data or {}
        self.api_message = self.data.get("api:message")
        self.api_statuscode = self.data.get("api:statuscode")
        self.api_duration = self.data.get("api:duration")
        self.api_timestamp = self.data.get("api:timestamp")