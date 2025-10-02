from orjson import loads, JSONDecodeError


class AminoError(Exception):
	"""
	Base class for all amino-related errors.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


class LibraryError(Exception):
	"""
	Base class for all library-related errors.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class DorksAPIError(Exception):
	"""
	Base class for all DorksAPI errors.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class DeprecatedFunction(LibraryError):
	"""
	Features that have stopped working and/or need fixing.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class UnknownError(LibraryError):
	"""
	Raised when the error code does not match anyone in the list.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


class InvalidProxyFormat(LibraryError):
	"""
	Raised when proxy type does not match the client type.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)




class SocketNotStarted(LibraryError):
	"""
	Raised when the socket is not running, but an attempt is made to interact with it.
	"""

class IncorrectType(LibraryError):
	"""
	Raised when the type of data passed to the function is incorrect.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class SpecifyType(LibraryError):
	"""
	Raised when you need to specify the output of the command.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class WrongType(LibraryError):
	"""
	Raised when you attribute the function the wrong type.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class NoCommunity(LibraryError):
	"""
	Raised when you try to make an action but no community was selected.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class AgeTooLow(LibraryError):
	"""
	Raised when you try to configure an account but the age is too low. Minimum is 13.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class UnsupportedLanguage(LibraryError):
	"""
	Raised when you try to use a language that isn't supported or exists.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class RequiredAuthorization(LibraryError):
	"""
	Raised when you are trying to perform an action that requires an account.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

#-----


class ServiceUnavailable(AminoError):
	"""
	- **Status Code** : 503
	- **API Message** : 503  Service unavailable.
	- **API String** : ``Unknown String``
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


class UnsupportedService(AminoError):
	"""
	- **API Code** : 100
	- **API Message** : Unsupported service. Your client may be out of date. Please update it to the latest version.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class FileTooLarge(AminoError):
	"""
	- **API Code** : 102
	- **API Message** : ``Unknown Message``
	- **API String** : API_STD_ERR_ENTITY_TOO_LARGE_RAW
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class InvalidRequest(AminoError):
	"""
	- **API Code** : 103, 104
	- **API Message** : Invalid Request. Please update to the latest version. If the problem continues, please contact us.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class InvalidSession(AminoError):
	"""
	- **API Code** : 105
	- **API Message** : ``Unknown Message``
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class AccessDenied(AminoError):
	"""
	- **API Code** : 106
	- **API Message** : Access denied.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class UnexistentData(AminoError):
	"""
	- **API Code** : 107
	- **API Message** : The requested data does not exist.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class ActionNotAllowed(AminoError):
	"""
	- **API Code** : 110
	- **API Message** : Action not allowed.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class ServiceUnderMaintenance(AminoError):
	"""
	- **API Code** : 111
	- **API Message** : Sorry, this service is under maintenance. Please check back later.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class MessageNeeded(AminoError):
	"""
	- **API Code** : 113
	- **API Message** : Be more specific, please.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class InvalidAccountOrPassword(AminoError):
	"""
	- **API Code** : 200
	- **API Message** : ``Unknown Message``
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class AccountDisabled(AminoError):
	"""
	- **API Code** : 210
	- **API Message** : This account is disabled.
	- **API String** : AUTH_DISABLED_ACCOUNT
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class InvalidEmail(AminoError):
	"""
	- **API Code** : 213
	- **API Message** : Invalid email address.
	- **API String** : API_ERR_EMAIL
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class InvalidPassword(AminoError):
	"""
	- **API Code** : 214
	- **API Message** : Invalid password. Password must be 6 characters or more and contain no spaces.
	- **API String** : API_ERR_PASSWORD
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class EmailAlreadyTaken(AminoError):
	"""
	- **API Code** : 215
	- **API Message** : Hey this email ``X`` has been registered already. You can try to log in with the email or edit the email.
	- **API String** : API_ERR_EMAIL_TAKEN
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class UnsupportedEmail(AminoError):
	"""
	- **API Code** : 215
	- **API Message** : This email address is not supported.
	- **API String** : API_ERR_EMAIL_TAKEN
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class AccountDoesntExist(AminoError):
	"""
	- **API Code** : 216
	- **API Message** : ``Unknown Message``
	- **API String** : AUTH_ACCOUNT_NOT_EXISTS
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class InvalidDevice(AminoError):
	"""
	- **API Code** : 218
	- **API Message** : Error! Your device is currently not supported, or the app is out of date. Please update to the latest version.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class TooManyRequests(AminoError):
	"""
	- **API Code** : 219
	- **API Message** 1) : Too many requests. Try again later.
	- **API Message** 2) : A maximum of 3 accounts can be created from this device. If you forget your password, please reset it.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class CantFollowYourself(AminoError):
	"""
	- **API Code** : 221
	- **API Message** : ``Unknown Message``
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class UserUnavailable(AminoError):
	"""
	- **API Code** : 225
	- **API Message** : This user is unavailable.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class YouAreBanned(AminoError):
	"""
	- **API Code** : 229
	- **API Message** : You are banned.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class UserNotMemberOfCommunity(AminoError):
	"""
	- **API Code** : 230
	- **API Message** : You have to join this Community first.
	- **API String** : API_ERR_USER_NOT_IN_COMMUNITY
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class RequestRejected(AminoError):
	"""
	- **API Code** : 235
	- **API Message** : Request rejected. You have been temporarily muted (read only mode) because you have received a strike. To learn more, please check the Help Center.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class ActivateAccount(AminoError):
	"""
	- **API Code** : 238
	- **API Message** : Please activate your account first. Check your email, including your spam folder.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class CantLeaveCommunity(AminoError):
	"""
	- **API Code** : 239
	- **API Message** : Sorry, you can not do this before transferring your Agent status to another member.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class ReachedTitleLength(AminoError):
	"""
	- **API Code** : 240
	- **API Message** : Sorry, the max length of member's title is limited to 20.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class AccountDeleted(AminoError):
	"""
	- **API Code** : 246
	- **API Message** : ``Unknown Message``
	- **API String** : AUTH_RECOVERABLE_DELETED_ACCOUNT
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class API_ERR_EMAIL_NO_PASSWORD(AminoError):
	"""
	- **API Code** : 251
	- **API Message** : ``Unknown Message``
	- **API String** : API_ERR_EMAIL_NO_PASSWORD
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class API_ERR_COMMUNITY_USER_CREATED_COMMUNITIES_VERIFY(AminoError):
	"""
	- **API Code** : 257
	- **API Message** : ``Unknown Message``
	- **API String** : API_ERR_COMMUNITY_USER_CREATED_COMMUNITIES_VERIFY
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class ReachedMaxTitles(AminoError):
	"""
	- **API Code** : 262
	- **API Message** : You can only add up to 20 Titles. Please choose the most relevant ones.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class VerificationRequired(AminoError):
	"""
	- **API Code** : 270
	- **API Message** : Verification Required.
	- **API String** : API_ERR_NEED_TWO_FACTOR_AUTHENTICATION
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class API_ERR_INVALID_AUTH_NEW_DEVICE_LINK(AminoError):
	"""
	- **API Code** : 271
	- **API Message** : ``Unknown Message``
	- **API String** : API_ERR_INVALID_AUTH_NEW_DEVICE_LINK
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class CommandCooldown(AminoError):
	"""
	- **API Code** : 291
	- **API Message** : Whoa there! You've done too much too quickly. Take a break and try again later.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class UserBannedByTeamAmino(AminoError):
	"""
	- **API Code** : 293
	- **API Message** : Sorry, this user has been banned by Team Amino.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class BadImage(AminoError):
	"""
	- **API Code** : 300
	- **API Message** : ``Unknown Message``
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class InvalidThemepack(AminoError):
	"""
	- **API Code** : 313
	- **API Message** : ``Unknown Message``
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class InvalidVoiceNote(AminoError):
	"""
	- **API Code** : 314
	- **API Message** : ``Unknown Message``
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class RequestedNoLongerExists(AminoError):
	"""
	- **API Code** : 500, 700, 1600
	- **API Message** : Sorry, the requested data no longer exists. Try refreshing the view.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class PageRepostedTooRecently(AminoError):
	"""
	- **API Code** : 503
	- **API Message** : Sorry, you have reported this page too recently.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class InsufficientLevel(AminoError):
	"""
	- **API Code** : 551
	- **API Message** : This post type is restricted to members with a level ``X`` ranking and above.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class WallCommentingDisabled(AminoError):
	"""
	- **API Code** : 702
	- **API Message** : This member has disabled commenting on their wall.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class CommunityNoLongerExists(AminoError):
	"""
	- **API Code** : 801
	- **API Message** : This Community no longer exists.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class InvalidCodeOrLink(AminoError):
	"""
	- **API Code** : 802
	- **API Message** : Sorry, this code or link is invalid.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class CommunityNameAlreadyTaken(AminoError):
	"""
	- **API Code** : 805
	- **API Message** : ``Unknown Message``
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class CommunityCreateLimitReached(AminoError):
	"""
	- **API Code** : 806
	- **API Message** : ``Unknown Message``
	- **API String** : API_ERR_COMMUNITY_USER_CREATED_COMMUNITIES_EXCEED_QUOTA
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class CommunityDisabled(AminoError):
	"""
	- **API Code** : 814
	- **API Message** : This Community is disabled.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class CommunityDeleted(AminoError):
	"""
	- **API Code** : 833
	- **API Message** : This Community has been deleted.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class DuplicatePollOption(AminoError):
	"""
	- **API Code** : 1501
	- **API Message** : Sorry, you have duplicate poll options.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class ReachedMaxPollOptions(AminoError):
	"""
	- **API Code** : 1507
	- **API Message** : Sorry, you can only join or add up to 5 of your items per poll.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class TooManyChats(AminoError):
	"""
	- **API Code** : 1602
	- **API Message** : Sorry, you can only have up to 1000 chat sessions.
	- **API String** : ``Unknown String``
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class ChatFull(AminoError):
	"""
	- **API Code** : 1605
	- **API Message** : ``Unknown Message``
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class TooManyInviteUsers(AminoError):
	"""
	- **API Code** : 1606
	- **API Message** : Sorry, you can only invite up to 999 people.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class ChatInvitesDisabled(AminoError):
	"""
	- **API Code** : 1611
	- **API Message** : This user has disabled chat invite requests.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class RemovedFromChat(AminoError):
	"""
	- **API Code** : 1612
	- **API Message** : You've been removed from this chatroom.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class UserNotJoined(AminoError):
	"""
	- **API Code** : 1613
	- **API Message** : Sorry, this user has not joined.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class API_ERR_CHAT_VVCHAT_NO_MORE_REPUTATIONS(AminoError):
	"""
	- **API Code** : 1627
	- **API Message** : ``Unknown Message``
	- **API String** : API_ERR_CHAT_VVCHAT_NO_MORE_REPUTATIONS
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class MemberKickedByOrganizer(AminoError):
	"""
	- **API Code** : 1637
	- **API Message** : This member was previously kicked by the organizer and cannot be reinvited.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class LevelFiveRequiredToEnableProps(AminoError):
	"""
	- **API Code** : 1661
	- **API Message** : ``Unknown Message``
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class ChatViewOnly(AminoError):
	"""
	- **API Code** : 1663
	- **API Message** : ``Unknown Message``
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class ChatMessageTooBig(AminoError):
	"""
	- **API Code** : 1664
	- **API Message** : ``Unknown Message``
	- **API String** : API_ERR_CHAT_MESSAGE_CONTENT_TOO_LONG
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class InviteCodeNotFound(AminoError):
	"""
	- **API Code** : 1900
	- **API Message** : Sorry, the requested data no longer exists. Try refreshing the view.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class AlreadyRequestedJoinCommunity(AminoError):
	"""
	- **API Code** : 2001
	- **API Message** : Sorry, you have already submitted a membership request.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class API_ERR_PUSH_SERVER_LIMITATION_APART(AminoError):
	"""
	- **API Code** : 2501
	- **API Message** : ``Unknown Message``
	- **API String** : API_ERR_PUSH_SERVER_LIMITATION_APART
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class API_ERR_PUSH_SERVER_LIMITATION_COUNT(AminoError):
	"""
	- **API Code** : 2502
	- **API Message** : ``Unknown Message``
	- **API String** : API_ERR_PUSH_SERVER_LIMITATION_COUNT
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class API_ERR_PUSH_SERVER_LINK_NOT_IN_COMMUNITY(AminoError):
	"""
	- **API Code** : 2503
	- **API Message** : ``Unknown Message``
	- **API String** : API_ERR_PUSH_SERVER_LINK_NOT_IN_COMMUNITY
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class API_ERR_PUSH_SERVER_LIMITATION_TIME(AminoError):
	"""
	- **API Code** : 2504
	- **API Message** : ``Unknown Message``
	- **API String** : API_ERR_PUSH_SERVER_LIMITATION_TIME
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class AlreadyCheckedIn(AminoError):
	"""
	- **API Code** : 2601
	- **API Message** : Sorry, you can't check in any more.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class AlreadyUsedMonthlyRepair(AminoError):
	"""
	- **API Code** : 2611
	- **API Message** : ``Unknown Message``
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class AccountAlreadyRestored(AminoError):
	"""
	- **API Code** : 2800
	- **API Message** : Account already restored.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class IncorrectVerificationCode(AminoError):
	"""
	- **API Code** : 3102
	- **API Message** : Incorrect verification code.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class NotOwnerOfChatBubble(AminoError):
	"""
	- **API Code** : 3905
	- **API Message** : You are not the owner of this chat bubble.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class NotEnoughCoins(AminoError):
	"""
	- **API Code** : 4300
	- **API Message** : ``Unknown Message``
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class AlreadyPlayedLottery(AminoError):
	"""
	- **API Code** : 4400
	- **API Message** : You have played the maximum number of lucky draws.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class CannotSendCoins(AminoError):
	"""
	- **API Code** : 4500, 4501
	- **API Message** : ``Unknown Message``
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class AminoIDAlreadyChanged(AminoError):
	"""
	- **API Code** : 6001
	- **API Message** : Amino ID cannot be changed after you set it.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class InvalidAminoID(AminoError):
	"""
	- **API Code** : 6002
	- **API Message** : Invalid Amino ID
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class InvalidName(AminoError):
	"""
	- **API Code** : 99001
	- **API Message** : Sorry, the name is invalid.
	- **API String** : ``Unknown String``
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class UserHasBeenDeleted(AminoError):
	"""
	- **API Code** : 245
	- **API Message** : Sorry, this user has been deleted.
	- **API String** : ``Unknown String``
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class IpTemporaryBan(AminoError):
	"""
	- **Status Code** : 403
	- **API Message** : 403 Forbidden.
	- **API String** : ``Unknown String``
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class FailedSubscribeFanClub(AminoError):
	"""
	- **API Code** : 4805
	- **API Message** : Failed to subscribe to this fan club.
	- **API String** : ``Unknown String``
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


exceptions_list = {
	"s503": ServiceUnavailable,
	"s403": IpTemporaryBan,
	100: UnsupportedService,
	102: FileTooLarge,
	103: InvalidRequest,
	104: InvalidRequest,
	105: InvalidSession,
	106: AccessDenied,
	107: UnexistentData,
	110: ActionNotAllowed,
	111: ServiceUnderMaintenance,
	113: MessageNeeded,
	200: InvalidAccountOrPassword,
	201: AccountDisabled,
	213: InvalidEmail,
	214: InvalidPassword,
	215: UnsupportedEmail,
	216: AccountDoesntExist,
	218: InvalidDevice,
	219: TooManyRequests,
	221: CantFollowYourself,
	225: UserUnavailable,
	229: YouAreBanned,
	230: UserNotMemberOfCommunity,
	235: RequestRejected,
	238: ActivateAccount,
	239: CantLeaveCommunity,
	240: ReachedTitleLength,
	245: UserHasBeenDeleted,
	246: AccountDeleted,
	251: API_ERR_EMAIL_NO_PASSWORD,
	257: API_ERR_COMMUNITY_USER_CREATED_COMMUNITIES_VERIFY,
	262: ReachedMaxTitles,
	270: VerificationRequired,
	271: API_ERR_INVALID_AUTH_NEW_DEVICE_LINK,
	291: CommandCooldown,
	293: UserBannedByTeamAmino,
	300: BadImage,
	313: InvalidThemepack,
	314: InvalidVoiceNote,
	500: RequestedNoLongerExists,
	503: PageRepostedTooRecently,
	551: InsufficientLevel,
	700: RequestedNoLongerExists,
	702: WallCommentingDisabled,
	801: CommunityNoLongerExists,
	802: InvalidCodeOrLink,
	805: CommunityNameAlreadyTaken,
	806: CommunityCreateLimitReached,
	814: CommunityDisabled,
	833: CommunityDeleted,
	1501: DuplicatePollOption,
	1507: ReachedMaxPollOptions,
	1600: RequestedNoLongerExists,
	1602: TooManyChats,
	1605: ChatFull,
	1606: TooManyInviteUsers,
	1611: ChatInvitesDisabled,
	1612: RemovedFromChat,
	1613: UserNotJoined,
	1627: API_ERR_CHAT_VVCHAT_NO_MORE_REPUTATIONS,
	1637: MemberKickedByOrganizer,
	1661: LevelFiveRequiredToEnableProps,
	1663: ChatViewOnly,
	1664: ChatMessageTooBig,
	1900: InviteCodeNotFound,
	2001: AlreadyRequestedJoinCommunity,
	2501: API_ERR_PUSH_SERVER_LIMITATION_APART,
	2502: API_ERR_PUSH_SERVER_LIMITATION_COUNT,
	2503: API_ERR_PUSH_SERVER_LINK_NOT_IN_COMMUNITY,
	2504: API_ERR_PUSH_SERVER_LIMITATION_TIME,
	2601: AlreadyCheckedIn,
	2611: AlreadyUsedMonthlyRepair,
	2800: AccountAlreadyRestored,
	3102: IncorrectVerificationCode,
	3905: NotOwnerOfChatBubble,
	4300: NotEnoughCoins,
	4400: AlreadyPlayedLottery,
	4500: CannotSendCoins,
	4501: CannotSendCoins,
	4805: FailedSubscribeFanClub,
	6001: AminoIDAlreadyChanged,
	6002: InvalidAminoID,
	9901: InvalidName
}

def check_exceptions(data : str, status : int) -> None:
	try:
		_data = loads(data)
		try:code = _data.get("api:statuscode")
		except:raise UnknownError(_data)
	except JSONDecodeError:
		if status == 503:code="s503"
		else:code="s403"
	if code in exceptions_list:raise exceptions_list[code](data)
	else:raise UnknownError(data)