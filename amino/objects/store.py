from .base_object import BaseObject

class WalletHistoryItem:
    def __init__(self, data: dict):
        self.data = data
        self.taxCoins = data.get("taxCoins")
        self.bonusCoinsFloat = data.get("bonusCoinsFloat")
        self.isPositive = data.get("isPositive")
        self.bonusCoins = data.get("bonusCoins")
        self.taxCoinsFloat = data.get("taxCoinsFloat")
        self.transanctionId = data.get("uid")
        self.changedCoins = data.get("changedCoins")
        self.totalCoinsFloat = data.get("totalCoinsFloat")
        self.changedCoinsFloat = data.get("changedCoinsFloat")
        self.sourceType = data.get("sourceType")
        self.createdTime = data.get("createdTime")
        self.totalCoins = data.get("totalCoins")
        self.originCoinsFloat = data.get("originCoinsFloat")
        self.originCoins = data.get("originCoins")
        self.extData: dict = data.get("extData", {})
        self.title = self.extData.get("description")
        self.description = self.extData.get("subtitle")
        self.icon = self.extData.get("icon")
        self.objectDeeplinkUrl = self.extData.get("objectDeeplinkUrl")
        self.sourceIp = self.extData.get("sourceIp")

class WalletInfo(BaseObject):


    def __init__(self, data: dict):

        class Coupon:
            def __init__(self, data: dict):
                self.couponId: str | None = data.get("couponId")
                self.couponType: int | None = data.get("couponType")
                self.couponValue: int | None = data.get("couponValue")
                self.createdTime: str | None = data.get("createdTime")
                self.expiredTime: str | None = data.get("expiredTime")
                self.expiredType: int | None = data.get("expiredType")
                self.modifiedTime: int | None = data.get("modifiedTime")
                self.scopeDesc: str | None = data.get("scopeDesc")
                self.status: int | None = data.get("status")
                self.title: str | None = data.get("title")


        super().__init__(data)

        wallet: dict = data.get("wallet", {})
        self.newUserCoupon: Coupon = Coupon(wallet.get("newUserCoupon", {}))
        self.adsEnabled: bool | None = wallet.get("adsEnabled")
        self.adsFlags: int | None = wallet.get("adsFlags")
        self.adsVideoStats: str | None = wallet.get("adsVideoStats")
        self.businessCoinsEnabled: bool | None = wallet.get("businessCoinsEnabled")
        self.totalBusinessCoins: bool | None = wallet.get("totalBusinessCoins")
        self.totalBusinessCoinsFloat: bool | None = wallet.get("totalBusinessCoinsFloat")
        self.totalCoins: bool | None = wallet.get("totalCoins")
        self.totalCoinsFloat: int | None = wallet.get("totalCoinsFloat")



class AminoMembershipInfo(BaseObject):


    def __init__(self, data: dict):
        super().__init__(data)

        self.accountMembershipEnabled: bool | None = data.get("accountMembershipEnabled")
        self.hasAnyAppleSubscription: bool | None = data.get("hasAnyAppleSubscription")
        self.hasAnyAndroidSubscription: bool | None = data.get("hasAnyAndroidSubscription")
        self.membership: str | None = data.get("membership")
        self.premiumFeatureEnabled: bool | None = data.get("premiumFeatureEnabled")



class AccountSubscription(BaseObject):


    def __init__(self, data: dict):
        super().__init__(data)

        self.subscriptionItemList: list = data.get("storeSubscriptionItemList", [])