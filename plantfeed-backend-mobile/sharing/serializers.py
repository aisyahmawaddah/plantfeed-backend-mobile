from rest_framework import serializers
from .models import Feed
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.authtoken.models import Token

class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ['Title', 'Message', 'Creator_id']