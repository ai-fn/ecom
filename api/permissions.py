from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnlyOrAdminPermission(BasePermission):
    """
    Разрешение, которое позволяет только чтение для всех пользователей, но полный доступ для администраторов.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True

        return request.method in SAFE_METHODS


class AllowCreateOrAdmin(BasePermission):

    def has_permission(self, request, view):
        return view.action == "create" or (request.user and request.user.is_staff)


class IsOwnerOrAdminPermission(BasePermission):
    """
    Разрешение, которое позволяет взаимодействовать с объектом только если пользователь является его владельцем.
    """
    
    def has_object_permission(self, request, view, obj):
        return is_owner_or_admin(request, obj)


class UserInfoPermission(BasePermission):
    """
    Пользователь может изменять или удалять объект только если он является его владельцем или админом.
    """

    def has_object_permission(self, request, view, obj):
        return obj.pk == request.user.pk or request.user.is_staff


def is_owner_or_admin(request, obj):
    obj_user = getattr(obj, "user", None) or getattr(obj, "customer", None) or getattr(obj, "owner", None)
    if not obj_user:
        raise AttributeError(f"'{obj.__class__.__name__}' object must have one of the attributes ('user', 'owner', 'customer').")

    return request.user == obj_user or request.user.is_staff
