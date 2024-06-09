from random import randint

PREFIX = bytes.fromhex("19")
SIG_KEY = bytes.fromhex("DFA5ED192DDA6E88A12FE12130DC6206B1251E44")
DEVICE_KEY = bytes.fromhex("E7309ECC0953C6FA60005B2765F99DBBC965C8E9")

host = "service.aminoapps.com"
api = f"https://{host}/api/v1"
ws_url = f"wss://ws{randint(1, 4)}.aminoapps.com"
ws_ping_interval = 3



community_modules = {
	"chat": "module.chat.enabled",
	"livechat": "module.chat.avChat.videoEnabled",
	"screeningroom": "module.chat.avChat.screeningRoomEnabled",
	"publicchats": "module.chat.publicChat.enabled",
	"posts": "module.post.enabled",
	"ranking": "module.ranking.enabled",
	"leaderboards": "module.ranking.leaderboardEnabled",
	"featured": "module.featured.enabled",
	"featuredposts": "module.featured.postEnabled",
	"featuredusers": "module.featured.memberEnabled",
	"featuredchats": "module.featured.publicChatRoomEnabled",
	"sharedfolder": "module.sharedFolder.enabled",
	"influencer": "module.influencer.enabled",
	"catalog": "module.catalog.enabled",
	"externalcontent": "module.externalContent.enabled",
	"topiccategories": "module.topicCategories.enabled"
}