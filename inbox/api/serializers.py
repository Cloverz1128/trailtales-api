from rest_framework import serializers
from notifications.models import Notification

def serialize_actor(actor):
    if actor is None:
        return None
    return {
        'id': actor.id,
        'type': actor.__class__.__name__.lower(),
        'name': getattr(actor, 'username', str(actor)),
        'url': f"/users/{actor.id}/"
    }


def serialize_target(target):
    if target is None:
        return None
    target_type = target.__class__.__name__.lower()
    return {
        'type': target_type,
        'id': target.id,
        'url': f"/{target_type}s/{target.id}/",
        'content': getattr(target, 'content', str(target)),
    }


class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id',
            'recipient',
            'actor',
            'verb',
            'target',
            'timestamp',
            'unread',
        ]                                                  

    def get_actor(self, obj):
        return serialize_actor(obj.actor)

    def get_target(self, obj):
        return serialize_target(obj.target)

    def get_recipient(self, obj):
        return {
            'id': obj.recipient.id,
            'username': obj.recipient.username
        }
