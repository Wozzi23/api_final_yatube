from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Собственный метод проверки доступа к обьектам модели
    с проверкой на соответсвие автора
    и пользователя сделавшего запрос
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
