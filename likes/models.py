from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from utils.memcached_helper import MemcachedHelper


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True
    )
    
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('user', 'content_type', 'object_id'),)
        index_together = (
            ('content_type', 'object_id', 'created_at'),
            ('user', 'content_type', 'created_at'), 
        )

    def __str__(self):
        return '{} - {} likes {} {}'.format(
            self.created_at,
            self.user,
            self.content_type,
            self.content_object,
        )
    
    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)