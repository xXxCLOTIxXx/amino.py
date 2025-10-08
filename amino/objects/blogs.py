from .user_profile import UserProfile
from .base_object import BaseObject

class Blog(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)

        if data.get("blog"): self.data = data.get("blog", {})

        author_data = self.data.get("author", {})
        self.author: UserProfile = UserProfile(author_data)

        quiz_data = self.data.get("quizQuestionList", {})
        self.quizQuestionList: list[QuizQuestion] = [QuizQuestion(x) for x in quiz_data]

        self.createdTime = self.data.get("createdTime")
        self.modifiedTime = self.data.get("modifiedTime")
        self.title = self.data.get("title")
        self.content = self.data.get("content")
        self.status = self.data.get("status")
        self.type = self.data.get("type")
        self.blogId = self.data.get("blogId")
        self.comId = self.data.get("ndcId")
        self.viewCount = self.data.get("viewCount")
        self.shareUrl = self.data.get("shareURLFullPath")
        self.keywords = self.data.get("keywords")
        self.mediaList = self.data.get("mediaList")
        self.style = self.data.get("style")
        self.contentRating = self.data.get("contentRating")
        self.needHidden = self.data.get("needHidden")
        self.widgetDisplayInterval = self.data.get("widgetDisplayInterval")
        self.endTime = self.data.get("endTime")
        self.refObjectId = self.data.get("refObjectId")
        self.refObject = self.data.get("refObject")
        self.votedValue = self.data.get("votedValue")
        self.votesCount = self.data.get("votesCount")
        self.globalVotesCount = self.data.get("globalVotesCount")
        self.globalVotedValue = self.data.get("globalVotedValue")
        self.guestVotesCount = self.data.get("guestVotesCount")
        self.globalCommentsCount = self.data.get("globalCommentsCount")
        self.commentsCount = self.data.get("commentsCount")
        self.totalPollVoteCount = self.data.get("totalPollVoteCount")
        self.totalQuizPlayCount = self.data.get("totalQuizPlayCount")

        tip_info = self.data.get("tipInfo", {})
        self.tipInfo = tip_info
        self.tippersCount = tip_info.get("tippersCount")
        self.tippable = tip_info.get("tippable")
        self.tippedCoins = tip_info.get("tippedCoins")

        extensions = self.data.get("extensions", {})
        self.extensions = extensions
        self.fansOnly = extensions.get("fansOnly")
        self.featuredType = extensions.get("featuredType")
        self.disabledTime = extensions.get("__disabledTime__")
        self.quizPlayedTimes = extensions.get("quizPlayedTimes")
        self.quizTotalQuestionCount = extensions.get("quizTotalQuestionCount")
        self.quizTrendingTimes = extensions.get("quizTrendingTimes")
        self.quizLastAddQuestionTime = extensions.get("quizLastAddQuestionTime")
        self.isIntroPost = extensions.get("isIntroPost")

        style_ext = extensions.get("style", {})
        self.backgroundColor = style_ext.get("backgroundColor")


class Wiki(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)

        if data.get("item"): self.data = data.get("item", {})

        self.author = UserProfile(self.data.get("author", {}))

        extensions = self.data.get("extensions", {})
        props = extensions.get("props", [])
        self.labels: list[WikiLabel] = [WikiLabel(x) for x in props]

        self.wikiId = self.data.get("itemId")
        self.status = self.data.get("status")
        self.style = self.data.get("style")
        self.globalCommentsCount = self.data.get("globalCommentsCount")
        self.modifiedTime = self.data.get("modifiedTime")
        self.votedValue = self.data.get("votedValue")
        self.globalVotesCount = self.data.get("globalVotesCount")
        self.globalVotedValue = self.data.get("globalVotedValue")
        self.contentRating = self.data.get("contentRating")
        self.title = self.data.get("label")
        self.content = self.data.get("content")
        self.keywords = self.data.get("keywords")
        self.needHidden = self.data.get("needHidden")
        self.guestVotesCount = self.data.get("guestVotesCount")
        self.votesCount = self.data.get("votesCount")
        self.comId = self.data.get("ndcId")
        self.createdTime = self.data.get("createdTime")
        self.mediaList = self.data.get("mediaList")
        self.commentsCount = self.data.get("commentsCount")
        self.extensions = extensions

        style_ext = extensions.get("style", {})
        self.backgroundColor = style_ext.get("backgroundColor")

        self.fansOnly = extensions.get("fansOnly")

        knowledge_base = extensions.get("knowledgeBase", {})
        self.knowledgeBase = knowledge_base
        self.version = knowledge_base.get("version")
        self.originalWikiId = knowledge_base.get("originalItemId")
        self.contributors = knowledge_base.get("contributors")


class WikiLabel:
    def __init__(self, data: dict):
        self.title = data.get("title")
        self.content = data.get("value")
        self.type = data.get("type")


class QuizQuestion:
    def __init__(self, data: dict):
        self.status = data.get("status")
        self.parentType = data.get("parentType")
        self.title = data.get("title")
        self.createdTime = data.get("createdTime")
        self.questionId = data.get("quizQuestionId")
        self.parentId = data.get("parentId")
        self.mediaList = data.get("mediaList")

        self.extensions = data.get("extensions", {})
        self.style = self.extensions.get("style", {})
        self.backgroundImage = None
        try:
            self.backgroundImage = self.style.get("backgroundMediaList", [])[0][1]
        except (IndexError, TypeError):
            pass

        self.backgroundColor = self.style.get("backgroundColor")
        self.answerExplanation = self.extensions.get("quizAnswerExplanation")

        opt_list = self.extensions.get("quizQuestionOptList", [])
        self.answersList: list[QuizAnswer] = [QuizAnswer(x) for x in opt_list]

class QuizAnswer:
    def __init__(self, data: dict):
        self.answerId = data.get("optId")
        self.qhash = data.get("qhash")
        self.isCorrect = data.get("isCorrect")
        self.mediaList = data.get("mediaList")
        self.title = data.get("title")
