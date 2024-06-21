class CommunityModules:
    """
    community modules (acm)
    
    attributes:

    - Chat
    - LiveChat
    - ScreeningRoom
    - PublicChats
    - Posts
    - Ranking
    - LeaderBoards
    - Featured
    - FeaturedPosts
    - FeaturedUsers
    - FeaturedChats
    - SharedFolder
    - Influencer
    - Catalog
    - ExternalContent
    - TopicCategories

    - all (list of all attributes)

    """

    Chat: str = "module.chat.enabled"
    LiveChat: str = "module.chat.avChat.videoEnabled"
    ScreeningRoom: str = "module.chat.avChat.screeningRoomEnabled"
    PublicChats: str = "module.chat.publicChat.enabled"
    Posts: str = "module.post.enabled"
    Ranking: str = "module.ranking.enabled"
    LeaderBoards: str = "module.ranking.leaderboardEnabled"
    Featured: str = "module.featured.enabled"
    FeaturedPosts: str = "module.featured.postEnabled"
    FeaturedUsers: str = "module.featured.memberEnabled"
    FeaturedChats: str = "module.featured.publicChatRoomEnabled"
    SharedFolder: str = "module.sharedFolder.enabled"
    Influencer: str = "module.influencer.enabled"
    Catalog: str = "module.catalog.enabled"
    ExternalContent: str = "module.externalContent.enabled"
    TopicCategories: str = "module.topicCategories.enabled"

    all: list = [
        Chat, LiveChat, ScreeningRoom, PublicChats, Posts,
        Ranking, LeaderBoards, Featured, FeaturedPosts,
        FeaturedUsers, FeaturedChats, SharedFolder, Influencer,
        Catalog, ExternalContent, TopicCategories
    ]