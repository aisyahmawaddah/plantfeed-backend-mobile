from rest_framework import serializers

from group.models import Group_tbl, GroupMembership, GroupTimeline, GroupTimelineComment, ReplyComment
from member.models import Person

from datetime import datetime

from datetime import datetime

from datetime import datetime

from sharing.models import Comment

class GroupSerializer(serializers.ModelSerializer):
    Admin_name = serializers.SerializerMethodField()
    Username_id = serializers.IntegerField()  # Change to read-write field
    
    class Meta:
        model = Group_tbl
        fields = ['id', 'Name', 'About', 'Media', 'Age', 'State', 'Username_id', 'Admin_name']

    def get_Admin_name(self, group):
        creator = group.Username
        return creator.Name

    def create(self, validated_data):
        username_id = validated_data.pop('Username_id')

        group = Group_tbl.objects.create(Username_id=username_id, **validated_data)

        # Create GroupMembership instance
        group_membership = GroupMembership.objects.create(GroupName=group, GroupMember=group.Username)

        # Save the group again to update any changes made in GroupMembership
        group.save()

        return group

class GroupMembershipSerializer(serializers.ModelSerializer):
    GroupName = serializers.CharField(source='GroupName.Name', read_only=True)
    Media = serializers.SerializerMethodField()
    About = serializers.SerializerMethodField()
    Username_id= serializers.SerializerMethodField()
    State = serializers.SerializerMethodField()
    # name = serializers.SerializerMethodField()
    # photo = serializers.SerializerMethodField()
    # username = serializers.SerializerMethodField()

    class Meta:
        model = GroupMembership
        fields = ['id', 'joined_on', 'GroupMember_id','GroupName_id', 'GroupName', 'Media', 'About', 'Username_id', 'State']

    def get_Media(self, obj):
        return obj.GroupName.Media.name if obj.GroupName.Media else ''

    def get_About(self, obj):
        return obj.GroupName.About if obj.GroupName.About else ''
    
    def get_Username_id(self, obj):
        return obj.GroupName.Username_id if obj.GroupName.Username_id else ''
    
    def get_State(self, obj):
        return obj.GroupName.State if obj.GroupName.State else ''
    
    # def get_name(self, obj):
    #     creator = Person.objects.get(id=obj.GroupMember_id)
    #     return creator.Name
    
    # def get_photo(self, obj):
    #     creator = Person.objects.get(id=obj.GroupMember_id)
    #     return creator.Photo.url
    
    # def get_username(self, obj):
    #     creator = Person.objects.get(id=obj.GroupMember_id)
    #     return creator.Username


from datetime import datetime

class GroupTimelineSerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()
    creator_photo = serializers.SerializerMethodField()
    creator_username = serializers.SerializerMethodField()
    Groupcreated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = GroupTimeline
        fields = ['id', 'GroupTitle', 'GroupMessage', 'GroupSkill', 'GroupState', 'GroupPhoto', 'GroupVideo', 'Groupcreated_at', 'CreatorFK_id', 'GroupFK_id', 'creator_name', 'creator_photo', 'creator_username']
        ordering = ['-Groupcreated_at']

    def get_creator_name(self, obj):
        creator = Person.objects.get(id=obj.CreatorFK_id)
        return creator.Name

    def get_creator_photo(self, obj):
        creator = Person.objects.get(id=obj.CreatorFK_id)
        return creator.Photo.url if creator.Photo else None

    def get_creator_username(self, obj):
        creator = Person.objects.get(id=obj.CreatorFK_id)
        return creator.Username

class GroupTimelineCommentSerializer(serializers.ModelSerializer):
    commenter_name = serializers.SerializerMethodField()
    commenter_photo = serializers.SerializerMethodField()
    commenter_username = serializers.SerializerMethodField()

    class Meta:
        model = GroupTimelineComment
        fields = ['id', 'GrpMessage', 'GrpVideo', 'GrpCommenterFK_id', 'GrpFeedFK_id', 'GrpPictures','commenter_name', 'commenter_photo', 'commenter_username']

    def get_commenter_name(self, obj):
        commenter = Person.objects.get(id=obj.GrpCommenterFK_id)
        return commenter.Name

    def get_commenter_photo(self, obj):
        commenter = Person.objects.get(id=obj.GrpCommenterFK_id)
        return commenter.Photo.url if commenter.Photo else None

    def get_commenter_username(self, obj):
        commenter = Person.objects.get(id=obj.GrpCommenterFK_id)
        return commenter.Username


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


class JoinedGroupSerializer(serializers.ModelSerializer):
    GroupName = serializers.CharField(source='GroupName.Name', read_only=True)
    Media = serializers.SerializerMethodField()
    About = serializers.SerializerMethodField()
    Username_id= serializers.SerializerMethodField()
    State = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = GroupMembership
        fields = ['id', 'joined_on', 'GroupMember_id','GroupName_id', 'GroupName', 'Media', 'About', 'Username_id', 'State' ,'name', 'photo', 'username']

    def get_Media(self, obj):
        return obj.GroupName.Media.name if obj.GroupName.Media else ''

    def get_About(self, obj):
        return obj.GroupName.About if obj.GroupName.About else ''
    
    def get_Username_id(self, obj):
        return obj.GroupName.Username_id if obj.GroupName.Username_id else ''
    
    def get_State(self, obj):
        return obj.GroupName.State if obj.GroupName.State else ''
    
    def get_name(self, obj):
        creator = Person.objects.get(id=obj.GroupMember_id)
        return creator.Name
    
    def get_photo(self, obj):
        creator = Person.objects.get(id=obj.GroupMember_id)
        return creator.Photo.url
    
    def get_username(self, obj):
        creator = Person.objects.get(id=obj.GroupMember_id)
        return creator.Username








