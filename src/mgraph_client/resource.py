from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any

import requests


class ManagedAttr:
    def __init__(self, is_readonly=True):
        self.is_readonly = is_readonly

    def __set_name__(self, owner, name):
        self._name = name
        names = name.split("_")
        self.name = "".join([names[0]] + [i.title() for i in names[1:]])

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return obj._data.get(self.name)
        except AttributeError:
            return None

    def __set__(self, obj, value):
        if self.is_readonly:
            raise AttributeError(f"Attribute '{self.name}' is read-only.")

    def __delete__(self, obj):
        if self.is_readonly:
            raise AttributeError(f"Attribute '{self.name}' is read-only.")


class SingleValueResource(ABC):

    URL = "https://graph.microsoft.com/v1.0"
    SELECT = True
    EXPAND = True
    FILTER = False
    ORDERBY = False
    TOP = False
    COUNT = False
    SEARCH = False

    GET = True
    POST = False
    PATCH = False
    DELETE = False

    _MODELS = {}

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls._MODELS[cls.__name__] = cls

    def __init__(
        self, client=None, data: dict[str, Any] | None = None, parent=None, **kwargs
    ):
        has_changed = True
        if data is None:
            data = {}

        self._client = client
        self._data = data
        self._parent = parent
        self._has_changed = has_changed
        self._query_params = {}
        self._get_response = None
        self._is_post = False

        self._set_kwargs(**kwargs)

    @property
    @abstractmethod
    def relative_endpoint(self):
        pass

    @property
    def url(self):
        return f"{self.URL}/{self.relative_endpoint}"

    @property
    def url_with_query_params(self):
        query_params = self.query_params
        if query_params:
            return f"{self.url}?{'&'.join(query_params)}"
        return self.url

    @property
    def query_params(self):
        return [f"${k}={v}" for k, v in self._query_params.items()]

    def get(self):
        if not self.GET:
            raise ValueError(f"Endpoint does not support GET method, '{self.url}'")
        if self._has_changed:
            response = requests.get(
                self.url_with_query_params, headers=self._client._headers
            )
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                print(response.json())
                raise
            self._data = response.json()
            self._has_changed = False
        return self

    def patch(self, data: dict[str, Any]):
        if not self.PATCH:
            raise ValueError(f"Endpoint does not support PATCH method, '{self.url}'")
        response = requests.patch(self.url, headers=self._client._headers, json=data)
        self._patch_response = response
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print(response.json())
            raise
        self._has_changed = True
        return self

    def delete(self, data: dict[str, Any]):
        if not self.DELETE:
            raise ValueError(f"Endpoint does not support DELETE method, '{self.url}'")
        response = requests.delete(self.url, headers=self._client._headers)
        self._delete_response = response
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print(response.json())
            raise
        self._has_changed = True
        return self

    def post(self, payload: dict[str, Any]):
        if not self.POST:
            raise ValueError(f"Endpoint does not support POST method, '{self.url}'")
        response = requests.post(self.url, headers=self._client._headers, json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print(response.json())
            raise
        self._has_changed = True
        return self

    def select(self, value: str):
        self._add_query_params("SELECT", value.strip())
        return self

    def expand(self, value: str):
        self._add_query_params("EXPAND", value.strip())
        return self

    def _add_query_params(self, key: str, value: str):
        if not getattr(self, key, False):
            raise ValueError(f"Query parameter is not supported, '{key}'.")
        self._query_params[key.lower()] = value.strip()
        self._has_changed = True

    def _set_kwargs(self, **kwargs):
        pass

    def asdict(self):
        return self._data


class MultiValueResource(SingleValueResource):

    FILTER = True
    ORDERBY = True
    TOP = True
    COUNT = True

    ITEM_CLASS = None

    def __init_subclass__(cls):
        if cls.ITEM_CLASS is None and not cls.STAND_ALONE:
            raise AttributeError(
                "Attribute 'ITEM_CLASS' is required if subclassing 'MultiValueResource'"
            )
        return super().__init_subclass__()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_page = 0
        self._objects = {}

    @property
    def current_page(self):
        return self._current_page + 1

    @property
    def current_items(self):
        current_page = self._current_page

        try:
            return self._objects[current_page]
        except KeyError:
            return list(self._iter_objects(current_page))

    def asdict(self):
        return self._data[self.current_page]["value"]

    def count_fetched_items(self):
        return sum([len(item["value"]) for item in self._data.values()])

    def has_next_items(self):
        return bool(self._data.get(self._current_page, {}).get("@odata.nextLink"))

    def get_next_items(self):
        current_page = self._current_page
        next_page = current_page + 1
        try:
            data = self._data[next_page]
        except KeyError:
            next_link = self._data[current_page].get("@odata.nextLink")
            if next_link:
                response = requests.get(next_link, headers=self._client._headers)

                try:
                    response.raise_for_status()
                except requests.HTTPError:
                    raise

                data = response.json()
                self._data[next_page] = data
            else:
                raise ValueError("No more items")

        self._current_page = next_page
        return self

    def iter_fetched_items(self):
        objects = self._objects

        for page in self._data:
            try:
                _iter_objects = iter(objects[page])
            except KeyError:
                yield from self._iter_objects(page)
            else:
                for obj in _iter_objects:
                    yield obj

    def iter_all_items(self):
        while self.has_next_items():
            self.get_next_items()
        else:
            yield from self.iter_fetched_items()

    def get(self):
        if not self.GET:
            raise ValueError(f"Endpoint does not support GET method, '{self.url}'")
        if self._has_changed:
            response = requests.get(
                self.url_with_query_params, headers=self._client._headers
            )
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                print(response.json())
                raise
            self._data.clear()
            self._objects.clear()
            self._has_changed = False
            self._data[0] = response.json()
        return self

    def filter(self, value: str):
        self._add_query_params("FILTER", value.strip())
        return self

    def filter__and(self, value: str):
        try:
            self._query_params["filter"] += f" and {value}"
        except KeyError:
            raise ValueError(
                f"Paremater does not exist. Can't append filter value, '{value}'"
            )
        return self

    def filter__or(self, value: str):
        try:
            self._query_params["filter"] += f" or {value}"
        except KeyError:
            raise ValueError(
                f"Paremater does not exist. Can't append filter value, '{value}'"
            )
        return self

    def orderby(self, value: str):
        self._add_query_params("ORDERBY", value.strip())
        return self

    def top(self, value: str | int):
        self._add_query_params("TOP", str(value).strip())
        return self

    def count(self):
        self._add_query_params("COUNT", "true")
        self._client._headers["ConsistencyLevel"] = "eventual"
        return self

    def _iter_objects(self, page):
        klass = self._MODELS[self.ITEM_CLASS]
        client = self._client

        page_objects = []
        page_objects_apppend = page_objects.append

        for item in self._data[page]["value"]:
            obj = klass(client, data=item, parent=self)
            page_objects_apppend(obj)
            yield obj

        self._objects[page] = page_objects
