from rest_framework import serializers
##tambah
from member.models import Person
from .models import Comment, Feed, ReplyComment
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.authtoken.models import Token

class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ['Title', 'Message', 'Creator_id']

#tambah

class FeedCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model= Comment 
        fields =['id', 'Message', 'Picture', 'Video', 'Commentor_id', 'Feed_id']


class FeedSerializerDetails(serializers.ModelSerializer):
    Profile_picture = serializers.SerializerMethodField()
    Creator_name = serializers.SerializerMethodField()
    Creator_username = serializers.SerializerMethodField()
    class Meta:
        model = Feed
        fields = ['id', "Creator_id",'Title','Message', 'Photo', "created_at","Creator_name","Profile_picture","Creator_username"]

    def get_Creator_name(self, feed):
        creator = Person.objects.get(id=feed.Creator_id)
        return creator.Name

    def get_Profile_picture(self, feed):
        creator = Person.objects.get(id=feed.Creator_id)
        return creator.Photo.url if creator.Photo else None
    
    def get_Creator_username(self, feed):
        creator = Person.objects.get(id=feed.Creator_id)
        return creator.Username
    

class CommentSerializer(serializers.ModelSerializer):
    Commenter_name = serializers.SerializerMethodField()
    Commenter_username = serializers.SerializerMethodField()
    Commenter_picture = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'Commenter_id','Feed_id','Message', 'Pictures', 'Video', 'Commenter_name', 'Commenter_username', 'Commenter_picture',]

    def create(self, validated_data):
        commenter_id = validated_data.pop('Commenter_id', None)
        # Perform the necessary steps to create a Comment instance
        comment = Comment.objects.create(**validated_data, Commenter_id=commenter_id)
        return comment

    def get_Commenter_name(self, comment):
        commenter = Person.objects.get(id=comment.Commenter_id)
        return commenter.Name
    
    def get_Commenter_username(self, comment):
        commenter = Person.objects.get(id=comment.Commenter_id)
        return commenter.Username
    
    def get_Commenter_picture(self, comment):
        commenter = Person.objects.get(id=comment.Commenter_id)
        return commenter.Photo.url if commenter.Photo else None


class PostCommentSerializer(serializers.ModelSerializer):
    message = serializers.CharField(source='Message')
    pictures = serializers.ImageField(source='Pictures', allow_null=True, required=False)
    video = serializers.FileField(source='Video', allow_null=True, required=False)
    commenter_id = serializers.IntegerField(source='Commenter_id')
    feed_id = serializers.IntegerField(source='Feed_id')

    class Meta:
        model = Comment
        fields = ('id', 'message', 'pictures', 'video', 'commenter_id', 'feed_id')

class ReplyCommentSerializer(serializers.ModelSerializer):
    Commenter_name = serializers.SerializerMethodField()
    Commenter_username = serializers.SerializerMethodField()
    Commenter_picture = serializers.SerializerMethodField()

    class Meta:
        model = ReplyComment
        fields = ['id', 'message', 'pictures', 'commenter_id', 'feed_id', 'comment_id', 'Commenter_name', 'Commenter_username', 'Commenter_picture']

    def create(self, validated_data):
        commenter_id = validated_data.pop('commenter_id', None)
        # Perform the necessary steps to create a ReplyComment instance
        reply_comment = ReplyComment.objects.create(**validated_data, commenter_id=commenter_id)
        return reply_comment

    def get_Commenter_name(self, reply_comment):
        commenter = Person.objects.get(id=reply_comment.commenter_id)
        return commenter.Name
    
    def get_Commenter_username(self, reply_comment):
        commenter = Person.objects.get(id=reply_comment.commenter_id)
        return commenter.Username
    
    def get_Commenter_picture(self, reply_comment):
        commenter = Person.objects.get(id=reply_comment.commenter_id)
        return commenter.Photo.url if commenter.Photo else None

