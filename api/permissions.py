from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnlyOrAdminPermission(BasePermission):
    """
    Разрешение, позволяющее только чтение для всех пользователей, 
    но полный доступ для администраторов.
    """

    def has_permission(self, request, view) -> bool:
        """
        Проверяет доступ для текущего запроса.

        :param request: Объект HTTP-запроса.
        :param view: Представление.
        :return: True, если разрешено, иначе False.
        """
        if request.user and request.user.is_staff:
            return True
        return request.method in SAFE_METHODS


class ReadCreateOrAdminPermission(BasePermission):
    """
    Разрешение для чтения и создания для всех аутентифицированных пользователей,
    а полный доступ для администраторов.
    """

    def has_permission(self, request, view) -> bool:
        """
        Проверяет доступ для текущего запроса.

        :param request: Объект HTTP-запроса.
        :param view: Представление.
        :return: True, если разрешено, иначе False.
        """
        if request.method in SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        if request.method == "POST":
            return True
        return request.user.is_staff


class AllowCreateOrAdmin(BasePermission):
    """
    Разрешение, которое позволяет создание объектов любым пользователям,
    а остальные действия только администраторам.
    """

    def has_permission(self, request, view) -> bool:
        """
        Проверяет доступ для текущего запроса.

        :param request: Объект HTTP-запроса.
        :param view: Представление.
        :return: True, если разрешено, иначе False.
        """
        return view.action == "create" or (request.user and request.user.is_staff)


class IsOwnerOrAdminPermission(BasePermission):
    """
    Разрешение, которое позволяет доступ к объекту, если пользователь является владельцем объекта или администратором.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Проверяет доступ к объекту.

        :param request: Объект HTTP-запроса.
        :param view: Представление.
        :param obj: Объект, к которому запрашивается доступ.
        :return: True, если разрешено, иначе False.
        """
        return is_owner_or_admin(request, obj)


class UserInfoPermission(BasePermission):
    """
    Разрешение, которое позволяет пользователю изменять или удалять объект,
    если он является владельцем объекта или администратором.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Проверяет доступ к объекту.

        :param request: Объект HTTP-запроса.
        :param view: Представление.
        :param obj: Объект, к которому запрашивается доступ.
        :return: True, если разрешено, иначе False.
        """
        return obj.pk == request.user.pk or request.user.is_staff


def is_owner_or_admin(request, obj) -> bool:
    """
    Проверяет, является ли пользователь владельцем объекта или администратором.

    :param request: Объект HTTP-запроса.
    :param obj: Объект, к которому запрашивается доступ.
    :return: True, если пользователь является владельцем или администратором.
    :rtype: bool
    :raises AttributeError: Если объект не имеет атрибутов `user`, `owner` или `customer`.
    """
    obj_user = getattr(obj, "user", None) or getattr(obj, "customer", None) or getattr(obj, "owner", None)
    if not obj_user:
        raise AttributeError(
            f"'{obj.__class__.__name__}' object must have one of the attributes ('user', 'owner', 'customer')."
        )

    return request.user == obj_user or request.user.is_staff
