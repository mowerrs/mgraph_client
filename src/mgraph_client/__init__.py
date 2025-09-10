import json

from msal import ConfidentialClientApplication, PublicClientApplication

from mgraph_client import directory_objects

from .resources import R
from .resources import Resource as _R

# from .groups import Groups
# from .service_principals import ServicePrincipals

# from .users import Users


class Resource:
    def __set_name__(self, owner, name) -> None:
        self.name = "".join(map(lambda x: x.title(), name.split("_")))

    def __get__(self, obj, objtype=None) -> R:
        klass = _R.MODELS[self.name]
        return klass(obj)

    def __set__(self, obj, value) -> None:
        raise AttributeError(f"Attribute '{self.name}' is read-only.")

    def __delete__(self, obj) -> None:
        raise AttributeError(f"Attribute '{self.name}' is read-only.")


class MgraphClient:

    device_management = Resource()
    directory_objects = Resource()
    drives = Resource()
    groups = Resource()
    sites = Resource()

    def __init__(
        self,
        client_id: str,
        tenant_id: str,
        client_secret: str | None = None,
        scopes: list[str] | None = None,
        _test: bool = False,
    ):
        if not _test:
            if client_secret:
                self._app = ConfidentialClientApplication(
                    client_id=client_id,
                    client_credential=client_secret,
                    authority=f"https://login.microsoftonline.com/{tenant_id}",
                )
            else:
                self._app = PublicClientApplication(client_id=client_id)

        if scopes is None:
            scopes = ["https://graph.microsoft.com/.default"]

        self._scopes = scopes

    @property
    def _access_token(self):
        result: dict[str, str] = self._app.acquire_token_for_client(scopes=self._scopes)  # type: ignore
        access_token = result.get("access_token")
        if access_token is None:
            raise ValueError(f"Failed to acquire token, {result}")

        return access_token

    @property
    def _headers(self):
        return {"Authorization": f"Bearer {self._access_token}"}

    # @property
    # def device_management(self) -> DeviceManagement:
    #     return DeviceManagement(self)

    # @property
    # def drives(self) -> Drives:
    #     return Drives(self)

    # @property
    # def groups(self):
    #     return Groups(self)

    # @property
    # def service_principals(self):
    #     return ServicePrincipals(self)

    # @property
    # def sites(self) -> Sites:
    #     return Sites(self)

    # @property
    # def users(self):
    #     return Users(self)


# class JsonDataStore:
#     def __init__(self, path):
#         with open(path, "r") as f:
#             self._data = json.load(f)
#         self._path = path

#     @property
#     def data(self):
#         return self._data

#     def save(self):
#         with open(self._path, "w") as f:
#             json.dump(self._data, f)
