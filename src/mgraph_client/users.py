from .resources import SingleValueResource, MultiValueResource, ManagedAttr


class Users(MultiValueResource):
    ITEM_CLASS = "User"

    @property
    def relative_endpoint(self):
        return "users"

    def by_id(self, user_id):
        return User(self._client, parent=self, user_id=user_id)


class User(SingleValueResource):

    id = ManagedAttr()
    display_name = ManagedAttr()
    user_principal_name = ManagedAttr()
    mail = ManagedAttr()
    account_enabled = ManagedAttr()

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}/{self._user_id}"

    @property
    def member_of(self):
        return MemberOf(self._client, parent=self)

    def _set_kwargs(self, user_id=None):
        _user_id = user_id or self._data.get("id")
        if _user_id is None:
            raise ValueError("Parameter is required, 'user_id'")
        self._user_id = _user_id


class MemberOf(MultiValueResource):

    ITEM_CLASS = "Group"

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}/memberOf"
