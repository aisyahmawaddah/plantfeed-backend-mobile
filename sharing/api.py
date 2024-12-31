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
    
#tambah 
@api_view(['GET'])
@permission_classes([])
def get_comments_by_feed(request, feed_id):
    try:
        comments = Comment.objects.filter(Feed_id=feed_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    except Comment.DoesNotExist:
        return Response(status=404)

@api_view(['POST'])
@permission_classes([AllowAny])
def postComment(request):
    serializer = PostCommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Comment Posted"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def replyComment(request):
    serializer = ReplyCommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Comment Posted"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CommentCreateAPIView(generics.CreateAPIView):
#     permission_classes = [AllowAny]
#     queryset = Comment.objects.all()
#     serializer_class = CommentSerializer
