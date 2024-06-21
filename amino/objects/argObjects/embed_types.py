
class EmbedTypes:
    """
    All possible values for Embed.

    attributes:

    - LINK_SNIPPET
    - ATTACHED_OBJECT
    """
    LINK_SNIPPET: int = 1
    ATTACHED_OBJECT: int = 2




class AttachedObjectTypes:
    """
    All possible values for Embed.

    - PROFILE
    - POST
    - WIKI
    - PUBLIC_CHAT
    """
    PROFILE: int = 0
    POST: int = 1
    WIKI: int  = 2
    PUBLIC_CHAT: int = 12