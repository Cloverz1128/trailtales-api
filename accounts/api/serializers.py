from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework import exceptions
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class UserSerializerForTweet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

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
        return user
