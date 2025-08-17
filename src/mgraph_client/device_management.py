from .resource import SingleValueResource, MultiValueResource


class DeviceManagement(SingleValueResource):

    GET = False

    @property
    def relative_endpoint(self):
        return "deviceManagement"

    @property
    def managed_devices(self):
        return ManagedDevices(self._client, parent=self)


class ManagedDevices(MultiValueResource):

    ITEM_CLASS = "ManagedDevice"

    @property
    def relative_endpoint(self):
        return f"{self._device_management.relative_endpoint}/managedDevices"

    def by_id(self, device_id: str):
        return ManagedDevice(self._client, parent=self, device_id=device_id)


class ManagedDevice(SingleValueResource):

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}/{self._device_id}"

    def _set_kwargs(self, device_id):
        self
        self._device_id = device_id
