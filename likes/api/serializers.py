from accounts.api.serializers import UserSerializerForLike
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from likes.models import Like
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializerForLike(source='cached_user')

    class Meta:
        model = Like
        fields = ('user', 'created_at')
    

class BaseLikeSerializerForCreateAndCancel(serializers.ModelSerializer):
    content_type = serializers.ChoiceField(choices=['comment', 'tweet'])
    object_id = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ('content_type', 'object_id')

    def _get_model_class(self, data):
        if data['content_type'] == 'comment':
            return Comment
        if data['content_type'] == 'tweet':
            return Tweet
        return None

    def validate(self, attrs):
        model_class = self._get_model_class(attrs)
        if model_class is None:
            raise ValidationError(
                {'content_type': 'Content type does not exist'})
        liked_object = model_class.objects.filter(id=attrs['object_id'])
        if not liked_object.exists():
            raise ValidationError({'object_id': 'object does not exists'})
        return attrs

class LikeSerializerForCreate(BaseLikeSerializerForCreateAndCancel):
    def get_or_create(self):
        validated_data = self.validated_data
        model_class = self._get_model_class(validated_data)
        return Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=validated_data['object_id'],
            user=self.context['request'].user,
        )

class LikeSerializerForCancel(BaseLikeSerializerForCreateAndCancel):
    def cancel(self):
        """
        cancel is a self designed function,  cancel will not call by serializer.save,
        need to call serializer.cancel() in views
        """
        model_class = self._get_model_class(self.validated_data) 
        deleted, _ = Like.objects.filter(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=self.validated_data['object_id'],
            user=self.context['request'].user
        ).delete()
        return deleted