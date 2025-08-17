from .resource import SingleValueResource, MultiValueResource, ManagedAttr
from . import directory_objects as do


class Groups(MultiValueResource):
    ITEM_CLASS = "Group"

    @property
    def relative_endpoint(self):
        return "groups"

    def by_id(self, group_id):
        return Group(self._client, parent=self, group_id=group_id)


class Group(SingleValueResource):

    PATCH = True

    id = ManagedAttr()
    description = ManagedAttr()
    display_name = ManagedAttr()
    mail_enabled = ManagedAttr()
    security_enabled = ManagedAttr()
    mail = ManagedAttr()
    mail_nickname = ManagedAttr()
    group_type = ManagedAttr()

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}/{self._group_id}"

    @property
    def members(self):
        return Members(self._client, parent=self)

    def _set_kwargs(self, group_id=None):
        _group_id = group_id or self._data.get("id")
        if _group_id is None:
            raise ValueError("Parameter is required, 'group_id'")
        self._group_id = _group_id


class Members(MultiValueResource):

    ITEM_CLASS = "User"

    class Reference(do.Reference):
        POST = True

        def get_payload_from_arg(self, dir_obj_id: str):
            return {"@odata.id": do.DirectoryObjects().by_id(dir_obj_id).url}

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}/members"

    @property
    def ref(self):
        return Members.Reference(self._client, parent=self)

    def by_directory_object_id(self, dir_obj_id: str):
        return DirectoryObject(self._client, parent=self, dir_obj_id=dir_obj_id)

    def get_payload_from_args(self, *args: str):
        dir_objs = do.DirectoryObjects()
        return {"members@odata.bind": [dir_objs.by_id(arg).url for arg in args]}


class DirectoryObject(do.DirectoryObject):
    class Reference(do.Reference):
        DELETE = True

    @property
    def ref(self):
        return DirectoryObject.Reference(self._client, parent=self)
