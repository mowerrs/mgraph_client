from .resources import MultiValueResource, SingleValueResource


class ServicePrincipals(MultiValueResource):

    ITEM_CLASS = "ServicePrincipal"

    @property
    def relative_endpoint(self):
        return "servicePrincipals"

    def by_service_principal_id(self, service_principal_id: str):
        return ServicePrincipal(
            self._client, parent=self, service_principal_id=service_principal_id
        )


class ServicePrincipal(SingleValueResource):

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}/{self._service_principal_id}"

    @property
    def app_role_assigned_to(self):
        return AppRoleAssignedTo(self._client, parent=self)

    def _set_kwargs(self, service_principal_id=None):
        self._service_principal = service_principal_id


class AppRoleAssignedTo(MultiValueResource):

    FILTER = False
    ORDERBY = False
    TOP = False
    COUNT = False
    SELECT = False
    EXPAND = False

    ITEM_CLASS = "_AppRoleAssignedTo"

    @property
    def relative_endpoint(self):
        return f"{self._parent.relative_endpoint}/appRoleAssignedTo"


class _AppRoleAssignedTo(SingleValueResource):

    SELECT = False
    EXPAND = False
    GET = False

    @property
    def relative_endpoint(self):
        return self._parent.relative_endpoint
