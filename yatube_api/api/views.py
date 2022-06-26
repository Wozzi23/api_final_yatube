from rest_framework import viewsets, filters, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (IsAuthenticated,
                                        AllowAny,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.viewsets import GenericViewSet

from api.permissions import IsAuthorOrReadOnly
from api.serializers import (PostSerializer,
                             GroupSerializer,
                             CommentSerializer,
                             FollowSerializer)
from posts.models import Post, Group, Comment, Follow, User


class PostViewSet(viewsets.ModelViewSet):
    """
    Модель обрабатывает запросы GET от любого пользователя,
    POST запросы доступны только зарегистрированному пользователю
    остальные методы PUT, PATCH, DELETE доступны только автору поста,
    реализован стандартный метод паджинации,
    через передачу у URL limit и offset.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly & IsAuthenticatedOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Модель обрабатывает только GET запросы от любого пользователя,
    изменение данных не доступно.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (AllowAny,)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Модель обрабатывает запросы GET от любого пользователя
    POST запросы доступны только зарегистрированному пользователю
    остальные методы PUT, PATCH, DELETE доступны только автору комментария,
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly & IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Получаем номер поста из URL запроса и
        этот обьект передаем в новый queryset
        """
        post_id = self.kwargs.get('post_id')
        new_queryset = Comment.objects.filter(post=post_id)
        return new_queryset

    def perform_create(self, serializer):
        """
        Функция сохранения комментария, пост получаем из URL запроса,
        поле author - пользователь сделавший запрос.
        """
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    """
    Модель подписки на авторов. Доступна только авторизованным пользователям,
    обрабатывает GET и POST запросы, иные действия не достуны. Реазован поиск
    по подпискам для этого необходимо в URL передать парамет search.
    """
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        """
        Получаем подписки пользователя сделавшего запрос
        и этот обьект передаем в new_queryset
        """
        new_queryset = Follow.objects.filter(user=self.request.user)
        return new_queryset

    def perform_create(self, serializer):
        """
        Функция сохранения подписки,
        поле user - пользователь сделавший запрос.
        """
        following = get_object_or_404(User,
                                      username=self.request.data['following'])
        serializer.save(user=self.request.user, following=following)
