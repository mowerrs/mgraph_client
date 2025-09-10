from typing import Any
from mgraph_client.resources import Resource


class DirectoryObjects(Resource):

    ITEM_CLASS = "DirectoryObject"

    @property
    def relative_endpoint(self):
        return "/directoryObjects"

    def by_id(self, dir_obj_id: str) -> "DirectoryObject":
        return DirectoryObject(self._client, parent=self, dir_obj_id=dir_obj_id)


class DirectoryObject(Resource):

    @property
    def relative_url(self) -> str:
        return f"/{self._dir_obj_id}"

    def _set_kwargs(self, kwargs: dict[str, Any]) -> None:
        dir_obj_id = kwargs.get("dir_obj_id")
        if dir_obj_id is None:
            raise ValueError("Parameter is required, 'dir_obj_id'")
        self._dir_obj_id = dir_obj_id


class Reference(Resource):

    @property
    def relative_url(self):
        return "/$ref"
