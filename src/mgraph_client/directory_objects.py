from mgraph_client.resource import SingleValueResource, MultiValueResource


class DirectoryObjects(MultiValueResource):

    ITEM_CLASS = "DirectoryObject"

    GET = False

    @property
    def relative_endpoint(self):
        return "directoryObjects"

    def by_id(self, dir_obj_id: str):
        return DirectoryObject(self._client, parent=self, dir_obj_id=dir_obj_id)


class DirectoryObject(SingleValueResource):

    GET = False

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}/{self._dir_obj_id}"

    def _set_kwargs(self, dir_obj_id=None):
        if dir_obj_id is None:
            raise ValueError("Parameter is required, 'dir_obj_id'")
        self._dir_obj_id = dir_obj_id


class Reference(SingleValueResource):

    SELECT = False
    EXPAND = False
    GET = False

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}/$ref"
