
class MediaObject:
    __slots__ = ("data", "mediaValue")
    
    def __init__(self, data: dict):
        if not data:
            for attr in self.__slots__:
                setattr(self, attr, None)
            return
        
        self.data = data
        self.mediaValue = data.get("mediaValue")