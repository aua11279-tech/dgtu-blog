from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Article, Tag, Profile


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ArticleSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Tag.objects.all(), source='tags'
    )

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'author',
            'tags', 'tag_ids', 'published_date', 'is_published'
        ]
        read_only_fields = ['author', 'published_date']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    user = AuthorSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'avatar', 'bio', 'birth_date']