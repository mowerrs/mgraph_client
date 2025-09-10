import json
from typing import Any

from mgraph_client.fields import CharField, DateTimeField

from .drives import DefaultDrive, Drives
from .resources import MultiValuedResource, Resource, SingleValuedResource


class Sites(MultiValuedResource):
    class RequestQueryParam(MultiValuedResource.RequestQueryParam):
        SEARCH = True
        FILTER = False
        ORDERBY = False

    class Root(SingleValuedResource):
        @property
        def relative_url(self) -> str:
            return "/root"

        def by_relative_path(self, relative_path) -> "SiteByRelativePath":
            return SiteByRelativePath(
                self._client, parent=self, relative_path=relative_path
            )

    ITEM_CLASS = "Site"

    @property
    def relative_url(self) -> str:
        # if self._by_relative_path:
        #     if self._hostname is None:
        #         raise ValueError(
        #             "Parameter 'hostname' is required if accessing by site relative path"
        #         )
        #     return f"/sites/{self._hostname}"

        return "/sites"

    def get(self) -> MultiValuedResource:
        if self._query_params.get("search") is None:
            raise ValueError(
                f"GET method is unsupported without search in query params"
            )

        return super().get()

    @property
    def root(self) -> "Sites.Root":
        return self.Root(client=self._client, parent=self)

    # def __call__(self, hostname: str):
    #     self._hostname = hostname
    #     return self

    def by_id(self, id) -> "Site":
        return SiteById(self._client, parent=self, site_id=id)

    # def by_relative_path(self, relative_path) -> type["Site"]:
    #     self._set_by(relative_path=True)
    #     return Site(self._client, parent=self, relative_path=relative_path)

    # def _set_by(self, id=False, relative_path=False):
    #     setattr(self, f"_by_id", id)
    #     setattr(self, f"_by_relative_path", relative_path)

    # def _set_kwargs(self, hostname=None, by_id=False, by_relative_path=False):
    #     self._hostname = hostname
    #     self._set_by(by_id, by_relative_path)


# class SiteRoot(SingleValueResource):

#     @property
#     def relative_endpoint(self) -> str:
#         return "sites/root"

#     def by_relative_path(self, relative_path) -> type["Site"]:
#         return Site(self._client, parent=self, relative_path=relative_path)


class Site(SingleValuedResource):
    id = CharField()
    description = CharField()
    name = CharField()
    web_url = CharField()
    display_name = CharField()
    created_date_time = DateTimeField()
    last_modified_date_time = DateTimeField()


class SiteById(Site):
    class DefaultDrive(DefaultDrive):
        @property
        def relative_url(self) -> str:
            return "/drive"

    id = CharField(fallback="site_id")

    @property
    def relative_url(self) -> str:
        return f"/{self._site_id}"

    @property
    def drive(self) -> "SiteById.DefaultDrive":
        return self.DefaultDrive(self._client, parent=self)

    # @property
    # def relative_endpoint(self) -> str:
    #     site_id = self.site_id
    #     if site_id:
    #         return f"sites/{site_id}"
    #     else:
    #         return f"{self._parent.relative_endpoint}:/{self._relative_path}"

    # @property
    # def lists(self) -> type["Lists"]:
    #     by_id = bool((self.site_id))
    #     if by_id:
    #         return Lists(self._client, parent=self, by_id=True)
    #     if self._relative_path:
    #         return Lists(self._client, parent=self, by_name=True)
    #     raise ValueError(
    #         "Arguments can't be both false, ('_site_id', '_relative_path')"
    #     )

    # @property
    # def site_id(self) -> str:
    #     return self._site_id or self.id

    # @property
    # def drives(self) -> Drives:
    #     return Drives(self._client, parent=self)

    # @property
    # def drive(self) -> DefaultDrive:
    #     if not bool(self.site_id):
    #         # Accessing default drive requires site id rather than a known relative path
    #         self.get()
    #     return DefaultDrive(self._client, parent=self)
    #     # if not self._drive_root:
    #     #     self._drive_root = None
    #     # return Drives(self._client, parent=self)

    # def _set_kwargs(self, site_id=None, relative_path=None):
    #     _site_id = site_id or self.id
    #     if not _site_id and not relative_path:
    #         raise ValueError("Parameter is required, 'site_id' or 'relative_path'")
    #     self._relative_path = relative_path
    #     self._site_id = _site_id

    def _set_kwargs(self, kwargs: dict[str, Any]) -> None:
        site_id = kwargs.get("site_id") or self.id
        if site_id is None:
            raise ValueError(
                "device_id is required by either setting the device_id or data argument"
            )
        self._site_id = site_id


class SiteByRelativePath(Site):
    class DefaultDrive(DefaultDrive):
        @property
        def relative_url(self) -> str:
            return ":/drive"

    @property
    def relative_url(self) -> str:
        return f":/{self._relative_path}"

    @property
    def drive(self) -> "SiteByRelativePath.DefaultDrive":
        return self.DefaultDrive(self._client, parent=self)

    def _set_kwargs(self, kwargs: dict[str, Any]) -> None:
        relative_path = kwargs.get("relative_path")
        if relative_path is None:
            raise ValueError("Argument is required, 'relative_path'")
        self._relative_path = relative_path


# class Lists(MultiValueResource):
#     ITEM_CLASS = "List"

#     @property
#     def relative_endpoint(self):
#         if self._by_name:
#             return f"{self._parent.relative_endpoint}:/lists"
#         return f"{self._parent.relative_endpoint}/lists"

#     def by_id(self, id):
#         self._set_by(id=True)
#         return List(self._client, parent=self, list_id=id)

#     def by_name(self, name):
#         self._set_by(name=True)
#         return List(self._client, parent=self, name=name)

#     def _set_by(self, id=False, name=False):
#         if id and name:
#             raise ValueError("Arguments can't be both true, ('id', 'name')")
#         setattr(self, f"_by_id", id)
#         setattr(self, f"_by_name", name)

#     def _set_kwargs(self, by_id=False, by_name=False):
#         self._set_by(by_id, by_name)


# class List(SingleValueResource):

#     id = ManagedAttr()
#     description = ManagedAttr()
#     name = ManagedAttr()
#     web_url = ManagedAttr()
#     display_name = ManagedAttr()
#     created_date_time = ManagedAttr()
#     last_modified_date_time = ManagedAttr()

#     @property
#     def relative_endpoint(self):
#         return f"{self._parent.relative_endpoint}/{self._key}"

#     @property
#     def items(self):
#         return ListItems(self._client, parent=self)

#     def _set_kwargs(self, name=None, list_id=None):
#         _name = name or self._data.get("name")
#         _list_id = list_id or self._data.get("id")

#         if not _name and not _list_id:
#             raise ValueError("Parameter is required, 'name' or 'list_id'")
#         self._key = _list_id or _name
#         self._name = name
#         self._list_id = _list_id


# class ListItems(MultiValueResource):

#     POST = True
#     ITEM_CLASS = "ListItem"

#     @property
#     def relative_endpoint(self):
#         return f"{self._parent.relative_endpoint}/items"

#     def by_id(self, id: int | str):
#         return ListItem(self._client, parent=self, item_id=id)


# class ListItem(SingleValueResource):

#     id = ManagedAttr()
#     created_date_time = ManagedAttr()
#     last_modified_date_time = ManagedAttr()
#     web_url = ManagedAttr()

#     @property
#     def relative_endpoint(self):
#         return f"{self._parent.relative_endpoint}/{self._item_id}"

#     @property
#     def fields(self):
#         return ListItemFields(self._client, parent=self)

#     def _set_kwargs(self, item_id=None):

#         data_id = self._data.get("id")
#         if not item_id and not data_id:
#             raise ValueError("Parameter is required, 'item_id'")
#         self._item_id = item_id or data_id

#     def download_attachment(self, field_name):
#         attachment = json.loads(self._data["fields"][field_name])
#         url = attachment["serverUrl"] + attachment["serverRelativeUrl"]
#         return requests.get(url, headers=self._client._headers)


# class ListItemFields(SingleValueResource):
#     PATCH = True

#     @property
#     def relative_endpoint(self):
#         return f"{self._parent.relative_endpoint}/fields"

#     def get(self):
#         parent = self._parent
#         try:
#             return parent._data["fields"]
#         except KeyError:
#             parent.get()
#         return parent._data["fields"]
