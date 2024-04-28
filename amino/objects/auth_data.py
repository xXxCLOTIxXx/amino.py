from ..helpers.generator import generate_user_agent, generate_deviceId

class auth_data:
    sid: str = None
    uid: str = None
    user_agent: str = None
    language: str = None 
    deviceId: str = None

    def __init__(self, deviceId: str = None, language: str = "en", user_agent: str = generate_user_agent()):
        self.deviceId = deviceId if deviceId else generate_deviceId()
        self.language = language
        self.user_agent = user_agent
