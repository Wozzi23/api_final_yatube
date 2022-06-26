from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from posts.models import Comment, Post, Group, Follow, User


class PostSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Post, поле author имеент значение
    по умолчанию в виде текущего пользователя сделавшего запрос.
    """
    author = serializers.StringRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id',
                  'author',
                  'text',
                  'pub_date',
                  'image',
                  'group',
                  )
        model = Post
        read_only_fields = ('author',)


class GroupSerializer(serializers.ModelSerializer):
    """"
    Сериализатор модели Grup.
    """
    class Meta:
        fields = ('id', 'title', 'slug', 'description',)
        model = Group


class CommentSerializer(serializers.ModelSerializer):
    """"
    Сериализатор модели Comment, поле author имеент значение
    по умолчанию в виде текущего пользователя сделавшего запрос,
    поле post передается из URL запроса пользователя.
    """
    author = serializers.StringRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = ('id', 'author', 'text', 'created', 'post',)
        model = Comment
        read_only_fields = ('author', 'post')


class FollowSerializer(serializers.ModelSerializer):
    """"
    Сериализатор модели Follow, поле user имеент значение
    по умолчанию в виде текущего пользователя сделавшего запрос.
    """
    user = serializers.StringRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        fields = ('user', 'following',)
        model = Follow
        read_only_fields = ('user',)
        validators = (
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            ),
        )

    def validate_following(self, following):
        """
        Проверка поля following,
        не дает в запросе POST подписаться на самого себя.
        """
        print(self.context.get('request').data['following'])
        if self.context.get('request').user == following:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')
        return following
