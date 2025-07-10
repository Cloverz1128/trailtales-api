def invalidate_following_cache(sender, instance, **kwargs):
    from friendships.services import FriendshipService # avoid loop import
    FriendshipService.invalidate_following_cache(instance.from_user_id)