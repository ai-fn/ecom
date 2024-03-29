from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnlyOrAdminPermission(BasePermission):
    """
    Разрешение, которое позволяет только чтение для всех пользователей, но полный доступ для администраторов.
    """

    def has_permission(self, request, view):
        # Проверка, является ли пользователь администратором
        if request.user and request.user.is_staff:
            return True

        # Проверка типа запроса: разрешить только запросы на чтение
        return request.method in SAFE_METHODS


class IsOwner(BasePermission):
    """
    Разрешение, которое позволяет только изменять или удалять объект только если он является его владельцем.
    """
    
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "customer") and request.user == obj.customer


class OwnerOrIsAdmin(BasePermission):
    """
    Пользователь может изменять или удалять объект только если он является его владельцем или админом.
    """

    def has_object_permission(self, request, view, obj):

        # Проверяем, является ли текущий пользователь владельцем объекта
        return obj.pk == request.user.pk or request.user.is_staff
