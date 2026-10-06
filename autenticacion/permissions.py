from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    roles = ()

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and any(hasattr(request.user, role) for role in self.roles))


class IsAgencia(RolePermission):
    roles = ('agencia',)


class IsProveedor(RolePermission):
    roles = ('proveedor',)


class IsTurista(RolePermission):
    roles = ('turista',)


class IsEmpresa(RolePermission):
    roles = ('agencia', 'proveedor')


class IsComprador(RolePermission):
    roles = ('turista', 'agencia')
