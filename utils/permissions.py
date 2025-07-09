from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        # when detail=True, self.get_object queryset get the obj
        return request.user == obj.user