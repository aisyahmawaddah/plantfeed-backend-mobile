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




