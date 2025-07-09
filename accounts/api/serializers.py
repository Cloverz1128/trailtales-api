from django.contrib.auth.models import User
from accounts.models import UserProfile
from rest_framework import serializers
from rest_framework import exceptions
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class UserSerializerWithProfile(UserSerializer):
    nickname = serializers.CharField(source='profile.nickname')
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        if obj.profile.avatar:
            return obj.profile.avatar.url
        return None

    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'avatar_url')

class UserProfileSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('nickname', 'avatar')

class UserSerializerForTweet(UserSerializerWithProfile):
    class Meta:
        model = User
        fields = ['id', 'username']

class UserSerializerForFriendship(UserSerializerWithProfile):
    class Meta:
        model = User
        fields = ['id', 'username']

class UserSerializerForComment(UserSerializerWithProfile):
    pass

class UserSerializerForLike(UserSerializerWithProfile):
    pass

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data['username'].lower()
        if not User.objects.filter(username=username).exists():
            raise ValidationError({'username': 'User does not exist.'})
        data['username'] = username
        return data

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email','password') 

    # will be called when is_valid is called
    def validate(self, data):  
        if User.objects.filter(username=data['username'].lower()).exists(): 
            raise ValidationError({  
                'message': 'This user name has been registered.'  
            })  
        if User.objects.filter(email=data['email'].lower()).exists():  
            raise ValidationError({  
                'message': 'This email has been occupied.'  
            })  
        return data
  
    def create(self, validated_data):  
        username = validated_data['username'].lower()  
        password = validated_data['password']  
        email = validated_data['email'].lower()  
  
        user = User.objects.create_user(  
            username=username,  
            password=password,  
            email=email  
        )  
        # Create User Profile object
        user.profile
        return user
