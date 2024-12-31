from django.db import models, migrations
# from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.syndication.views import Feed
from member.models import Person, SoilTag, PlantTag

# Create your models here.

class Group_tbl(models.Model):
    
    Name = models.CharField(max_length=150)
    About = models.CharField(max_length=1000)
    Media = models.ImageField(upload_to='uploads/',default="")
    Username = models.ForeignKey(Person, on_delete=models.CASCADE)
    Age = models.CharField(max_length=100,default="")
    State = models.CharField(max_length=100,default="")

    def save(self):
        # group = self
        super().save()
        #super().save(using='farming')
        # return group
        return self.id
    
    
        
    def deleteRecordIgrow(self):
        super().delete()
    
    class Meta:
        db_table = 'group_tbl'
        
class pl_graph_api(models.Model):
    
    name = models.CharField(max_length=255)
    embed_link = models.CharField(max_length=255)
    chart_type = models.CharField(max_length=255)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    Person_fk = models.ForeignKey(Person, on_delete=models.CASCADE)
    
    def save(self):
        super().save()
        
class pl_graph_sharing(models.Model):
    
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1500)
    link = models.CharField(max_length=255)
    chart_type = models.CharField(max_length=255, null=True)
    Group_fk = models.ForeignKey(Group_tbl, on_delete=models.CASCADE)
    Person_fk = models.ForeignKey(Person, on_delete=models.CASCADE)
    
    def save(self):
        super().save()

class GroupMembership(models.Model):
    
    GroupName = models.ForeignKey(Group_tbl, on_delete=models.CASCADE)
    GroupMember = models.ForeignKey(Person, on_delete=models.CASCADE)
    # joined_on = models.DateTimeField(default=datetime.now, blank=True)
    joined_on = models.DateTimeField(auto_now_add=True, blank=True)

    def save(self):
        super().save()

    
    class Meta:
        
        unique_together = [['GroupName', 'GroupMember']]


class GroupSoilTagging(models.Model):

    GroupSoilTag = models.ForeignKey(Group_tbl, related_name="soilTagging", on_delete=models.CASCADE)    
    soilTag = models.ForeignKey(SoilTag, on_delete=models.CASCADE)
   
    class Meta:  
        unique_together = [['GroupSoilTag', 'soilTag']]

    def save(self):
        super().save()
   
    def deleteRecordIgrow(self):
        super().delete()


class GroupPlantTagging(models.Model):

    GroupPlantTag = models.ForeignKey(Group_tbl, related_name="plantTagging", on_delete=models.CASCADE)    
    plantTag = models.ForeignKey(PlantTag, on_delete=models.CASCADE)
   
    class Meta:  
        unique_together = [['GroupPlantTag', 'plantTag']]

    def save(self):
        super().save()
   
    def deleteRecordIgrow(self):
        super().delete()

class GroupTimeline(models.Model):
    id = models.AutoField(primary_key=True)
    GroupTitle = models.CharField(max_length=100)
    GroupMessage = models.TextField()
    GroupSkill = models.CharField(max_length=100)
    GroupState = models.CharField(max_length=100)
    GroupPhoto = models.ImageField(upload_to='group_photos/', null=True, blank=True)
    GroupVideo = models.FileField(upload_to='group_videos/', null=True, blank=True)
    Groupcreated_at = models.DateTimeField(auto_now_add=True)
    CreatorFK_id = models.IntegerField()  # Assuming CreatorFK_id is an integer field
    GroupFK_id = models.IntegerField()  # Assuming GroupFK_id is an integer field

    def __str__(self):
        return self.GroupTitle

    class Meta:
        db_table = 'grouptimeline'

class GroupTimelineComment(models.Model):
    id = models.AutoField(primary_key=True)
    GrpMessage = models.TextField()
    GrpPictures= GrpVideo = models.FileField(upload_to='group_comment_pictures/', null=True, blank=True)
    GrpVideo = models.FileField(upload_to='group_comment_videos/', null=True, blank=True)
    GrpCommenterFK_id = models.IntegerField()
    GrpFeedFK_id = models.IntegerField()

    def __str__(self):
        return f"Comment #{self.id} for Feed #{self.GrpFeedFK_id}"

    class Meta:
        db_table = 'grouptimelinecomment'


class ReplyComment(models.Model):
    
    message = models.CharField(max_length=8000)
    pictures = models.ImageField(upload_to='reply_comment_images', null=True, blank=True)
    # video = models.FileField(upload_to='reply_comment_videos', null=True, blank=True)
    commenter_id = models.IntegerField()
    comment_id = models.IntegerField()
    feed_id = models.IntegerField()

    def __str__(self):
        return f"ReplyComment {self.id}"


