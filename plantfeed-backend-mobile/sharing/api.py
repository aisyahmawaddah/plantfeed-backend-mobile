from ast import Delete
from rest_framework import generics
import json
from pyexpat import model
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

@api_view(['POST'])
@permission_classes([AllowAny])
def postFeed(request):
    """
    Create a new post.
    """
    serializer = FeedSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Feed Posted"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreatorFeedView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, creator_id):
        feeds = Feed.objects.filter(Creator_id=creator_id)
        serializer = FeedSerializer(feeds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)