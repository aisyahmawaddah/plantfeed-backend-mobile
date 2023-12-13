from django.db import models
from django.db import models, migrations
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.syndication.views import Feed
from datetime import datetime
from group.models import Group_tbl
from member.models import Person, SoilTag, PlantTag

# Create your models here.


class Feed(models.Model):
    class Meta:
        db_table = 'Feed'
    Title = models.CharField(max_length=255)
    Message = models.CharField(max_length=255)
    Skill = models.CharField(max_length=20,default="")
    State = models.CharField(max_length=100,default="")
    Photo = models.ImageField(upload_to ='uploads/', blank=True,null=True, default="")
    #Video = models.FileField(upload_to='uploads/', blank=True, null=True, default="")
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    #Creator_id = models.IntegerField()
    #Group = models.ForeignKey(Group_tbl, on_delete=models.CASCADE)
    Creator = models.ForeignKey(Person, on_delete=models.CASCADE)
    #Links = models.CharField(max_length=255)


    def save(self):
        super().save()
        #super().save(using='farming')
        return self.id

    def deleteRecordIgrow(self):
        super().delete()

class GroupTimeline(models.Model):
    class Meta:
        db_table = 'GroupTimeline'
    GroupTitle = models.CharField(max_length=255)
    GroupMessage = models.CharField(max_length=255)
    GroupSkill = models.CharField(max_length=20,default="")
    GroupState = models.CharField(max_length=100,default="")
    GroupPhoto = models.ImageField(upload_to ='uploads/', blank=True,null=True, default="")
    #GroupVideo = models.FileField(upload_to='uploads/', blank=True, null=True, default="")
    Groupcreated_at = models.DateTimeField(default=datetime.now, blank=True)
    GroupFK = models.ForeignKey(Group_tbl, on_delete=models.CASCADE)
    CreatorFK = models.ForeignKey(Person, on_delete=models.CASCADE)


    def save(self):
        super().save()
        return self.id
        
    def deleteRecordIgrow(self):
        super().delete()
    

class Comment(models.Model):
    class Meta:
        db_table = 'Comment'    
    Message = models.TextField()
    Pictures = models.ImageField(upload_to='uploads/', null=True)
    #Video = models.FileField(upload_to='uploads/', null=True)
    Feed = models.ForeignKey(Feed, related_name="comments", on_delete=models.CASCADE)
    Commenter = models.ForeignKey(Person, on_delete=models.CASCADE)

    def save(self):
        super().save()
        return self.id

        
    def deleteRecordIgrow(self):
        super().delete()

class Likes(models.Model):
    class Meta:
        db_table = 'Likes'    
    #Like = models.IntegerField()
    Feed = models.ForeignKey(Feed, related_name="likes", on_delete=models.CASCADE)
    Liker = models.ForeignKey(Person, on_delete=models.CASCADE)

    def save(self):
        super().save()
        return self.id

        
    def deleteRecordIgrow(self):
        super().delete()

class GroupTimelineComment(models.Model):
    class Meta:
        db_table = 'GroupTimelineComment'    
    GrpMessage = models.TextField()
    GrpPictures = models.ImageField(upload_to='uploads/', null=True)
    #GrpVideo = models.FileField(upload_to='uploads/', null=True)
    GrpFeedFK = models.ForeignKey(GroupTimeline, related_name="groupcomments", on_delete=models.CASCADE)
    GrpCommenterFK = models.ForeignKey(Person, on_delete=models.CASCADE)

    def save(self):
        super().save()
        return self.id
        
    def deleteRecordIgrow(self):
        super().delete()


class FeedSoilTagging(models.Model):

    FeedSoilTag = models.ForeignKey(Feed, related_name="soilTagging", on_delete=models.CASCADE)    
    soilTag = models.ForeignKey(SoilTag, on_delete=models.CASCADE)
    
    class Meta:  
        unique_together = [['FeedSoilTag', 'soilTag']]

    def save(self):
        super().save()
        
        
    def deleteRecordIgrow(self):
        super().delete()


class FeedPlantTagging(models.Model):

    FeedPlantTag = models.ForeignKey(Feed, related_name="plantTagging", on_delete=models.CASCADE)    
    plantTag = models.ForeignKey(PlantTag, on_delete=models.CASCADE)
   
    class Meta:  
        unique_together = [['FeedPlantTag', 'plantTag']]

    def save(self):
        super().save()

        
    def deleteRecordIgrow(self):
        super().delete()

class GFeedSoilTagging(models.Model):

    FeedSoilTag = models.ForeignKey(GroupTimeline, related_name="soilTagging", on_delete=models.CASCADE)    
    soilTag = models.ForeignKey(SoilTag, on_delete=models.CASCADE)
    
    class Meta:  
        unique_together = [['FeedSoilTag', 'soilTag']]

    def save(self):
        super().save()
        
        
    def deleteRecordIgrow(self):
        super().delete()


class GFeedPlantTagging(models.Model):

    FeedPlantTag = models.ForeignKey(GroupTimeline, related_name="plantTagging", on_delete=models.CASCADE)    
    plantTag = models.ForeignKey(PlantTag, on_delete=models.CASCADE)
   
    class Meta:  
        unique_together = [['FeedPlantTag', 'plantTag']]

    def save(self):
        super().save()

        
    def deleteRecordIgrow(self):
        super().delete()


