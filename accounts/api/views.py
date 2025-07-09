from django.contrib.auth.models import User, Group
from accounts.models import UserProfile
from utils.permissions import IsObjectOwner
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.api.serializers import (
    UserSerializer, 
    LoginSerializer,
    RegisterSerializer,
    UserSerializerWithProfile,
    UserProfileSerializerForUpdate
)
from django.contrib.auth import (
    logout as django_logout,
    login as django_login,
    authenticate as django_auth
)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializerWithProfile
    permission_classes = (permissions.IsAdminUser,)

class AccountViewSet(viewsets.ViewSet):
    serializer_class = RegisterSerializer
	
    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        data = {'has_logged_in': request.user.is_authenticated,
                'ip_address': request.META['REMOTE_ADDR']}  
        if request.user.is_authenticated:  
            data['username'] = LoginSerializer(request.user).data
        return Response(data)
    
    @action(methods=['POST'], detail = False)
    def logout(self, request):
        django_logout(request)
        return Response({'success': True})

    @action(methods=['POST'], detail=False)
    def login(self, request):
        # get username and password
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():  
            return Response({  
                "success": False,  
                "message": "Please check input",  
                "errors": serializer.errors,  
            }, status=400)  

        username = serializer.validated_data['username']  
        password = serializer.validated_data['password']
        
        # validation ok, login
        user = django_auth(username=username, password=password)  
        if not user or user.is_anonymous:  
            return Response({  
                "success": False,  
                "message": "username and password does not match",  
            }, status=400)  
        
        django_login(request, user) #generate and set login cookie and session
        return Response({  
            "success": True,  
            "user": UserSerializer(instance=user).data
        })
    
    @action(methods=['POST'], detail=False)
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({  
                "success": False,  
                "message": "Please check input.",  
                "errors": serializer.errors,
            }, status=400)
        
        user = serializer.save()
        django_login(request, user)
        return Response({  
            "success": True,  
            "user": UserSerializer(instance=user).data
        }, status=201)
    
# PUT api/profiles/<id> -> profile_id not user_id
class UserProfileViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.UpdateModelMixin,
):
    queryset = UserProfile
    permission_classes = (permissions.IsAuthenticated, IsObjectOwner,)
    serializer_class = UserProfileSerializerForUpdate