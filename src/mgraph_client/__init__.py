import json

from msal import ConfidentialClientApplication, PublicClientApplication

from .device_management import DeviceManagement
from .drives import Drives
from .groups import Groups
from .service_principals import ServicePrincipals
from .sites import Sites
from .users import Users


class MgraphClient:

    def __init__(
        self,
        client_id: str,
        tenant_id: str,
        client_secret: str | None = None,
        scopes: list[str] | None = None,
        _test=False,
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
        result = self._app.acquire_token_for_client(scopes=self._scopes)
        access_token = result.get("access_token")
        if access_token is None:
            raise ValueError(f"Failed to acquire token, {result}")

        return access_token

    @property
    def _headers(self):
        return {"Authorization": f"Bearer {self._access_token}"}

    @property
    def device_management(self):
        return DeviceManagement(self)

    @property
    def drives(self):
        return Drives(self)

    @property
    def groups(self):
        return Groups(self)

    @property
    def service_principals(self):
        return ServicePrincipals(self)

    @property
    def sites(self):
        return Sites(self)

    @property
    def users(self):
        return Users(self)


class JsonDataStore:
    def __init__(self, path):
        with open(path, "r") as f:
            self._data = json.load(f)
        self._path = path

    @property
    def data(self):
        return self._data

    def save(self):
        with open(self._path, "w") as f:
            json.dump(self._data, f)
