from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import IntegerField
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
