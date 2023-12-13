
from datetime import datetime
from django.db import models, migrations
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.syndication.views import Feed
from member.models import Person, SoilTag, PlantTag

# Create your models here.

class Workshop(models.Model):
    class Meta:
        db_table = 'Workshop'
    ProgrammeName = models.CharField(max_length=150,default="")
    Speaker=models.CharField(max_length=150, default="")
    Description=models.CharField(max_length=150,default="")
    Date = models.DateField()
    RegistrationDue = models.DateField()
    Gender = models.CharField(max_length=20,default="")
    StartTime = models.TimeField()
    EndTime = models.TimeField()
    State = models.CharField(max_length=100,default="")
    Venue = models.CharField(max_length=100,default="")
    Poster = models.ImageField(upload_to='uploads/',default="")
    #RegistrationDue = models.DateField()
    # Session = models.CharField(max_length=150)
    # nanti next version or bila share version ni, sila remove null=true okay
    PIC = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True)

    def save(self):
        super().save()
        return self.id

    
    def deleteRecordIgrow(self):
        super().delete()
        
   
class WorkshopSharing(models.Model):
    class Meta:
        db_table = 'WorkshopSharing'
    Title = models.CharField(max_length=255)
    Message = models.CharField(max_length=255)
    #Skill = models.CharField(max_length=20,default="")
    #State = models.CharField(max_length=100,default="")
    Photo = models.ImageField(upload_to ='uploads/', blank=True,null=True, default="")
    #Video = models.FileField(upload_to='uploads/', blank=True, null=True, default="")
    #created_at = models.DateTimeField(default=datetime.now, blank=True)
    #Creator_id = models.IntegerField()
    #Group = models.ForeignKey(Group_tbl, on_delete=models.CASCADE)
    Creator = models.ForeignKey(Person, on_delete=models.CASCADE)
    Workshop_id = models.ForeignKey(Workshop, on_delete=models.CASCADE)
    #Links = models.CharField(max_length=255)


    def save(self):
        super().save()
        #super().save(using='farming')
        return self.id

    def deleteRecordIgrow(self):
        super().delete()



class Booking(models.Model):
    class Meta:
        db_table = 'Booking'
    # Name = models.CharField(max_length=150)
    ProgrammeName = models.CharField(max_length=150,default="")
    Date = models.DateField()
    # Session = models.CharField(max_length=150)
    # nanti next version or bila share version ni, sila remove null=true okay
    BookWorkshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, null=True)
    Participant = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True)
    Messages = models.CharField(max_length=250, default="",null=True)

    def save(self):
        super().save()
        
        
    def deleteRecordIgrow(self):
        super().delete()
    
    class Meta:
        
        unique_together = [['BookWorkshop', 'Participant']]

class Inbox(models.Model):
    class Meta:
        db_table = 'inbox'
    Messages = models.CharField(max_length=250, default="",null=True)
    WorkshopTitle = models.CharField(max_length=250, default="",null=True)
    Participant = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    #WorkshopFk = models.ForeignKey(Workshop, on_delete=models.CASCADE, null=True)
    is_read = models.BooleanField(default=False)

    def save(self):
        super().save()
        
    def deleteRecordIgrow(self):
        super().delete()

class WorkshopSoilTagging(models.Model):

    WorkshopSoilTag = models.ForeignKey(Workshop, related_name="soilTagging", on_delete=models.CASCADE)    
    soilTag = models.ForeignKey(SoilTag, on_delete=models.CASCADE)
   
    class Meta:  
        unique_together = [['WorkshopSoilTag', 'soilTag']]

    def save(self):
        super().save()
        
    def deleteRecordIgrow(self):
        super().delete()


class WorkshopPlantTagging(models.Model):

    WorkshopPlantTag = models.ForeignKey(Workshop, related_name="plantTagging", on_delete=models.CASCADE)    
    plantTag = models.ForeignKey(PlantTag, on_delete=models.CASCADE)
   
    class Meta:  
        unique_together = [['WorkshopPlantTag', 'plantTag']]

    def save(self):
        super().save()
        
    def deleteRecordIgrow(self):
        super().delete()

