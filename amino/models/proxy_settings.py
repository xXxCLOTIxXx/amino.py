


class SocketProxy:
    def __init__(self, proxy_type: str = None, http_proxy_host: str = None, http_proxy_port: str = None, http_proxy_auth: tuple = None):
        self.proxy_type=proxy_type
        self.http_proxy_host=http_proxy_host
        self.http_proxy_port=http_proxy_port
        self.http_proxy_auth=http_proxy_auth