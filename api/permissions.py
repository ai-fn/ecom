
from rest_framework import permissions

class ReadOnlyOrAdminPermission(permissions.BasePermission):
    """
    Разрешение, которое позволяет только чтение для всех пользователей, но полный доступ для администраторов.
    """

    def has_permission(self, request, view):
        # Проверка, является ли пользователь администратором
        if request.user and request.user.is_staff:
            return True

        # Проверка типа запроса: разрешить только запросы на чтение
        return request.method in permissions.SAFE_METHODS


class ReadOnlyOrIsOwnerOrIsAdmin(permissions.BasePermission):
    """
    Пользователь может изменять или удалять объект только если он является его владельцем.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD, OPTIONS запросы, т.е. только чтение
        if request.method in permissions.SAFE_METHODS:
            return True

        # Проверяем, является ли текущий пользователь владельцем объекта
        return obj.pk == request.user.pk or request.user.is_staff
