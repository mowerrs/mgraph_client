import json

import requests

from .resource import ManagedAttr, SingleValueResource, MultiValueResource
from .drives import Drives


class Sites(MultiValueResource):
    SEARCH = True
    ITEM_CLASS = "Site"

    @property
    def relative_endpoint(self):
        if self._by_relative_path:
            if self._hostname is None:
                raise ValueError(
                    "Parameter 'hostname' is required if accessing by site relative path"
                )
            return f"sites/{self._hostname}"

        return "sites"

    @property
    def root(self):
        return SiteRoot(client=self._client)

    def __call__(self, hostname: str):
        self._hostname = hostname
        return self

    def by_id(self, id):
        self._set_by(id=True)
        return Site(self._client, parent=self, id=id)

    def by_relative_path(self, relative_path):
        self._set_by(relative_path=True)
        return Site(self._client, parent=self, relative_path=relative_path)

    def _set_by(self, id=False, relative_path=False):
        setattr(self, f"_by_id", id)
        setattr(self, f"_by_relative_path", relative_path)

    def _set_kwargs(self, hostname=None, by_id=False, by_relative_path=False):
        self._hostname = hostname
        self._set_by(by_id, by_relative_path)


class SiteRoot(SingleValueResource):

    @property
    def relative_endpoint(self):
        return "sites/root"

    def by_relative_path(self, relative_path):
        return Site(self._client, parent=self, relative_path=relative_path)


class Site(SingleValueResource):

    id = ManagedAttr()
    description = ManagedAttr()
    name = ManagedAttr()
    web_url = ManagedAttr()
    display_name = ManagedAttr()
    created_date_time = ManagedAttr()
    last_modified_date_time = ManagedAttr()

    @property
    def relative_endpoint(self):
        site_id = self._site_id or self.id
        if site_id:
            return f"sites/{site_id}"
        else:
            return f"{self._parent.relative_endpoint}:/{self._relative_path}"

    @property
    def lists(self):
        return Lists(self._client, parent=self)

    @property
    def drives(self):
        return Drives(self._client, parent=self)

    def _set_kwargs(self, site_id=None, relative_path=None):
        _site_id = site_id or self._data.get("id")
        if not _site_id and not relative_path:
            raise ValueError("Parameter is required, 'site_id' or 'relative_path'")
        self._relative_path = relative_path
        self._site_id = _site_id


class Lists(MultiValueResource):
    ITEM_CLASS = "List"

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}:/lists"

    def by_name(self, name):
        return List(self._client, parent=self, name=name)

    def by_id(self, id):
        return List(self._client, parent=self, list_id=id)


class List(SingleValueResource):

    id = ManagedAttr()
    description = ManagedAttr()
    name = ManagedAttr()
    web_url = ManagedAttr()
    display_name = ManagedAttr()
    created_date_time = ManagedAttr()
    last_modified_date_time = ManagedAttr()

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}/{self._key}"

    @property
    def items(self):
        return ListItems(self._client, parent=self)

    def _set_kwargs(self, name=None, list_id=None):
        _name = name or self._data.get("name")
        _list_id = list_id or self._data.get("id")

        if not _name and not _list_id:
            raise ValueError("Parameter is required, 'name' or 'list_id'")
        self._key = _list_id or _name
        self._name = name
        self._list_id = _list_id


class ListItems(MultiValueResource):

    POST = True
    ITEM_CLASS = "ListItem"

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}/items"

    def by_id(self, id: int | str):
        return ListItem(self._client, parent=self, item_id=id)


class ListItem(SingleValueResource):

    id = ManagedAttr()
    created_date_time = ManagedAttr()
    last_modified_date_time = ManagedAttr()
    web_url = ManagedAttr()

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}/{self._item_id}"

    @property
    def fields(self):
        return ListItemFields(self._client, parent=self)

    def _set_kwargs(self, item_id=None):

        data_id = self._data.get("id")
        if not item_id and not data_id:
            raise ValueError("Parameter is required, 'item_id'")
        self._item_id = item_id or data_id

    def download_attachment(self, field_name):
        attachment = json.loads(self._data["fields"][field_name])
        url = attachment["serverUrl"] + attachment["serverRelativeUrl"]
        return requests.get(url, headers=self._client._headers)


class ListItemFields(SingleValueResource):
    PATCH = True

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}/fields"

    def get(self):
        parent = self._parent
        try:
            return parent._data["fields"]
        except KeyError:
            parent.get()
        return parent._data["fields"]
