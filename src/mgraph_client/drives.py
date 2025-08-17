from .resource import ManagedAttr, SingleValueResource, MultiValueResource


class Drives(MultiValueResource):

    ITEM_CLASS = "Drive"

    @property
    def relative_endpoint(self):
        parent = self._parent
        if isinstance(parent, Drives._MODELS["Site"]):
            if parent.id is None:
                parent.get()
            return f"{self._parent.relative_endpoint}/drives"
        else:
            return "drives"

    def by_id(self, drive_id: str):
        return Drive(self._client, parent=self, drive_id=drive_id)


class Drive(SingleValueResource):
    SELECT = False
    EXPAND = False

    id = ManagedAttr()
    created_date_time = ManagedAttr()
    description = ManagedAttr()
    drive_type = ManagedAttr()
    last_modified_date_time = ManagedAttr()
    name = ManagedAttr()
    web_url = ManagedAttr()

    class Items(SingleValueResource):
        SELECT = False
        EXPAND = False

        @property
        def relative_endpoint(self):
            return f"{self._parent.relative_endpoint}/items"

        def by_id(self, item_id: str):
            return DriveItem(self._client, parent=self, item_id=item_id)

        def from_data(self, data):
            return DriveItem(self._client, parent=self, data=data)

    @property
    def relative_endpoint(self):
        return f"drives/{self.id or self._drive_id}"

    @property
    def items(self):
        return Drive.Items(self._client, parent=self)

    @property
    def root(self):
        return DriveItemRoot(self._client, parent=self)

    def _set_kwargs(self, drive_id):
        self._drive_id = drive_id


class DriveItemRoot(SingleValueResource):
    SELECT = False
    EXPAND = False
    SEARCH = True

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}/root"

    def by_relative_path(self, relative_path: str):
        return DriveItem(self._client, parent=self, relative_path=relative_path)

    @property
    def children(self):
        return DriveItemChildren(self._client, parent=self)

    def search_with_q(self, value: str):
        return DriveItemChildren(
            self._client, parent=self, path_relation=f"/search(q='{value}')"
        )


class DriveItem(SingleValueResource):
    created_date_time = ManagedAttr()
    id = ManagedAttr()
    last_modified_date_time = ManagedAttr()
    name = ManagedAttr()
    web_url = ManagedAttr()
    size = ManagedAttr()
    parent_reference = ManagedAttr()

    @property
    def relative_endpoint(self):
        if self._item_id:
            return f"{self._parent.relative_endpoint}/{self._item_id}"
        return f"{self._parent.relative_endpoint}:/{self._relative_path}"

    @property
    def children(self):
        if self._relative_path:
            return DriveItemChildren(
                self._client, parent=self, path_relation=":/children"
            )
        return DriveItemChildren(self._client, parent=self)

    def search_with_q(self, value: str):
        return DriveItemChildren(
            self._client, parent=self, path_relation=f"/search(q='{value}')"
        )

    def _set_kwargs(self, item_id=None, relative_path=None):
        self._item_id = item_id or self.id
        self._relative_path = relative_path


class DriveItemChildren(MultiValueResource):
    ITEM_CLASS = "DriveItem"

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}{self._path_relation}"

    def _set_kwargs(self, path_relation=None):
        self._path_relation = path_relation or "/children"

    def _iter_objects(self, page):
        page_objects = []
        page_objects_apppend = page_objects.append

        for item in self._data[page]["value"]:
            drive = Drive(self._client, drive_id=item["parentReference"]["driveId"])
            obj = drive.items.from_data(item)
            page_objects_apppend(obj)
            yield obj

        self._objects[page] = page_objects
