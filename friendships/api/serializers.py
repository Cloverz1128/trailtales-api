from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from accounts.api.serializers import UserSerializerForFriendship

from friendships.models import Friendship

class FollowerSerializer(ModelSerializer):
    user = UserSerializerForFriendship(source='from_user')

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')

class FollowingSerializer(ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')
    
    class Meta:
        model = Friendship
        fields = ('user', 'created_at')

class FriendshipSerialierForCreate(ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'You can not follow yourself.'
            })
        return attrs

    def creat(self, validated_data):
        Friendship.objects.create(
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id'],
        )