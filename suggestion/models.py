from django.db import models
from datetime import datetime

class ChatBot(models.Model):
    class Meta:
        db_table = 'Chatbot'
    Question = models.CharField(max_length=255)
    Answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    
    def save(self):
        super().save()
        #super().save(using='farming')
        return self.id

    def deleteRecordIgrow(self):
        super().delete()