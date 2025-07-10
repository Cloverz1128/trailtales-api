from friendships.models import Friendship

class FriendshipService(object):

    @classmethod
    def get_follower_ids(cls, user):

        friendships = Friendship.objects.filter(to_user=user)
        follower_ids = [friendship.from_user_id for friendship in friendships]
        
        return follower_ids
    
        # followers = User.objects.filter(id__in=follower_ids)
        # return followers
    
        # friendships = Friendship.objects.filter(
        #     to_user=user,
        # ).prefetch_related('from_user') # in query
        # return [friendship.from_user for friendship in friendships]

    @classmethod
    def has_followed(self, from_user, to_user):
        return Friendship.objects.filter(
            from_user=from_user,
            to_user=to_user,
        ).exists()
