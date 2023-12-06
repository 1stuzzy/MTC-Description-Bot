from aiogram.types import CallbackQuery
from aiogram.dispatcher.filters import BoundFilter

from Package.models import User


class IsUserFilter(BoundFilter):
    key = "is_user"

    def __init__(self, is_user):
        self.is_user = is_user

    def get_target(self, obj):
        return getattr(obj, "from_user", None)

    async def check(self, obj):
        user = self.get_target(obj)
        if user:
            exists = User.select().where(User.cid == user.id).exists()
            return exists == self.is_user
        return False


class IsAdminFilter(BoundFilter):
    key = "is_admin"
    def __init__(self, is_admin):
        self.is_admin = is_admin

    def get_target(self, obj):
        return getattr(obj, "from_user", None)

    async def check(self, obj):
        user = self.get_target(obj)
        try:
            user = User.get(cid=user.id)
            if self.is_admin == (user.status >= 3):
                return {"user": user}
        except User.DoesNotExist:
            return not self.is_admin


class Access_Filter(BoundFilter):
    key = "access"

    def __init__(self, access):
        self.access = access

    def get_target(self, obj):
        return getattr(obj, "from_user", None)

    async def check(self, obj):
        user = self.get_target(obj)
        try:
            user = User.get(cid=user.id)
            if self.access == (user.access == 1):
                return {"user": user}
        except User.DoesNotExist:
            return not self.access
