from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from friendships.listeners import invalidate_following_cache
from utils.memcached_helper import MemcachedHelper

class Friendship(models.Model):
    from_user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="following_friendship_set"
    )
    to_user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="follower_friendship_set"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('from_user_id', 'created_at'),
            ('to_user_id', 'created_at')
        )
        unique_together = (('from_user_id', 'to_user_id'),)
        ordering = ('-created_at', )
        
    def __str__(self):
        return f'{self.from_user.id} followed {self.to_user.id}'
    
    @property
    def cached_from_user(self):
         return MemcachedHelper.get_object_through_cache(User, self.from_user_id)
    
    @property
    def cached_to_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.to_user_id)

# hook up with listeners to invalidate cache
pre_delete.connect(invalidate_following_cache, sender=Friendship)
post_save.connect(invalidate_following_cache, sender=Friendship)