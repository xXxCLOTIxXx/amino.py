class VoiceChatJoinPermissions:
    Open: int = 1
    ApprovalRequired: int = 2
    InviteOnly: int = 3

    all: tuple = (Open, ApprovalRequired, InviteOnly)
