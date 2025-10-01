

class BaseObject:
    api_message: str | None
    api_statuscode: str | None
    api_duration: str | None
    api_timestamp: str | None
    data: dict | list

    def __init__(self, data: dict | list):
        if isinstance(data, dict):
            self.api_message = data.get("api:message")
            self.api_statuscode = data.get("api:statuscode")
            self.api_duration = data.get("api:duration")
            self.api_timestamp = data.get("api:timestamp")