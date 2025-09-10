from typing import TYPE_CHECKING, Any

from .fields import CharField, DateTimeField, IntegerField
from .resources import MultiValuedResource, R, Resource, SingleValuedResource

if TYPE_CHECKING:
    from mgraph_client import MgraphClient


# https://learn.microsoft.com/en-us/graph/api/resources/onedrive?view=graph-rest-1.0


# https://learn.microsoft.com/en-us/graph/api/drive-list?view=graph-rest-1.0&tabs=http
class Drives(Resource):

    @property
    def relative_url(self):
        # parent = self._parent
        # if isinstance(parent, Drives._MODELS["Site"]):
        #     if parent.id is None:
        #         parent.get()
        #     return f"{parent.relative_endpoint}/drives"
        # else:
        return "/drives"

    def by_id(self, drive_id: str) -> "Drive":
        return Drive(self._client, parent=self, drive_id=drive_id)


# https://learn.microsoft.com/en-us/graph/api/drive-get?view=graph-rest-1.0&tabs=http
class DefaultDrive(SingleValuedResource):

    id = CharField(fallback="drive_id")
    created_date_time = DateTimeField()
    description = CharField()
    drive_type = CharField()
    last_modified_date_time = DateTimeField()
    name = CharField()
    web_url = CharField()

    @property
    def relative_url(self) -> str:
        return "/drive"

    # @property
    # def url(self) -> str:
    #     parent = self._parent
    #     if parent is None:
    #         return f"{self.URL}{self.relative_url}"
    #     parent.get()
    #     return f"{parent.url}{self.relative_url}"

    @property
    def root(self) -> "RootDriveItem":
        return RootDriveItem(self._client, parent=self)


class Drive(DefaultDrive):

    class DriveItems(Resource):

        @property
        def relative_url(self) -> str:
            return "/items"

        def by_id(self, item_id: str) -> "DriveItem":
            return DriveItem(self._client, parent=self, item_id=item_id)

    @property
    def relative_url(self) -> str:
        return f"/{self._drive_id}"

    @property
    def items(self) -> "DriveItems":
        return self.DriveItems(self._client, parent=self)

    # @property
    # def root(self) -> "DriveRoot":
    #     return DriveRoot(self._client, parent=self)

    def _set_kwargs(self, kwargs: dict[str, Any]) -> None:
        _drive_id = kwargs.get("drive_id") or self.id
        if _drive_id is None:
            raise ValueError(
                "drive_id is required and by setting a drive_id or data argument."
            )
        self._drive_id = _drive_id

    # def from_data(self, data) -> "DriveItem":
    #     return DriveItem(self._client, parent=self, data=data)

    # @property
    # def root(self) -> "DriveRoot":
    #     return DriveRoot(self._client, parent=self)
    #     # return Site.DriveRoot(self._client, parent=self)

    # def by_path(self, item_path: str) -> "DriveByRelativePath":
    #     return DriveByRelativePath(self._client, parent=self, item_path=item_path)

    # @property
    # def children(self) -> "DriveItemChildren":
    #     return DriveItemChildren(self._client, parent=self)

    # def search_with_q(self, value: str) -> "DriveItemChildren":
    #     return DriveItemChildren(
    #         self._client, parent=self, path_relation=f"/search(q='{value}')"
    #     )


# https://learn.microsoft.com/en-us/graph/api/driveitem-get?view=graph-rest-1.0&tabs=http
class DriveItem(SingleValuedResource):

    class RequestQueryParam(SingleValuedResource.RequestQueryParam):
        SEARCH = True

    class Children(MultiValuedResource):
        class RequestQueryParam(MultiValuedResource.RequestQueryParam):
            FILTER = False
            TOP = True

        ITEM_CLASS = "DriveItem"

        @property
        def relative_url(self):
            return f"/children"

        def _get_obj(
            self, klass: type[R], client: "MgraphClient", data: dict[str, Any]
        ) -> R:
            drive_items = client.drives.by_id(data["parentReference"]["driveId"]).items
            return klass(client, data=data, parent=drive_items)

    created_date_time = DateTimeField()
    id = CharField(fallback="item_id")
    last_modified_date_time = DateTimeField()
    name = CharField()
    web_url = CharField()
    size = IntegerField()
    parent_reference = CharField()

    @property
    def relative_url(self):
        return f"/{self._item_id}"

    @property
    def children(self) -> "DriveItem.Children":
        return self.Children(self._client, parent=self)

    def by_relative_path(self, relative_path: str) -> "DriveByRelativePath":
        return DriveByRelativePath(
            self._client, parent=self, relative_path=relative_path
        )

    def _set_kwargs(self, kwargs: dict[str, Any]) -> None:
        _item_id = kwargs.get("item_id") or self.id
        if _item_id is None:
            raise ValueError(
                "item_id is required by either setting item_id or data argument"
            )
        self._item_id = _item_id


class RootDriveItem(DriveItem):

    @property
    def relative_url(self) -> str:
        return "/root"

    def by_relative_path(self, relative_path: str) -> "DriveByRelativePath":
        return DriveByRelativePath(
            self._client, parent=self, relative_path=relative_path
        )

    def _set_kwargs(self, kwargs: dict[str, Any]) -> None:
        pass


class DriveByRelativePath(DriveItem):

    class Children(DriveItem.Children):
        @property
        def relative_url(self):
            return f":/children"

    @property
    def relative_url(self) -> str:
        return f":/{self._relative_path}"

    # @property
    # def children(self) -> "DriveItemChildren":
    #     return DriveItemChildren(self._client, parent=self, path_relation=":/children")

    def _set_kwargs(self, kwargs: dict[str, Any]) -> None:
        _relative_path = kwargs.get("relative_path")
        if _relative_path is None:
            raise ValueError("Argument is required, relative_path")
        self._relative_path = _relative_path


# class DriveItemChildren(MultiValuedResource):
#     ITEM_CLASS = "DriveItem"

#     @property
#     def relative_url(self):
#         return f"/children"

#     # def _set_kwargs(self, path_relation=None):
#     #     self._path_relation = path_relation or "/children"

#     # def _iter_objects(self, page):
#     #     page_objects = []
#     #     page_objects_apppend = page_objects.append

#     #     for item in self._data[page]["value"]:
#     #         drive = Drive(self._client, drive_id=item["parentReference"]["driveId"])
#     #         obj = drive.items.from_data(item)
#     #         page_objects_apppend(obj)
#     #         yield obj

#     #     self._objects[page] = page_objects

#     # def _get_obj(self, client, klass, data):
#     #     drive = Drive(client, drive_id=data["parentReference"]["driveId"])
#     #     return drive.items.from_data(data)
