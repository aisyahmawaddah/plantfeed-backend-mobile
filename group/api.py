from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group_tbl
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
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
from group.serializers import GroupSerializer
class GroupList(APIView):
    permission_classes =[AllowAny]
    def get(self, request):
        groups = Group_tbl.objects
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status =status.HTTP_200_OK)

# Create new group
@api_view(['POST'])
@permission_classes([AllowAny])
def createGroup(request):
    serializer = GroupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message:" "Group Created"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_group_membership(request):
    if request.method == 'POST':
        # Get the data from the request
        data = request.data

        # Extract the values from the data
        group_name_id = data.get('GroupName_id')
        group_member_id = data.get('GroupMember_id')
        joined_on = datetime.now()

        # Create a new GroupMembership instance
        group_membership = GroupMembership(
            GroupName_id=group_name_id,
            GroupMember_id=group_member_id,
            joined_on=joined_on
        )

        try:
            # Save the new GroupMembership object
            group_membership.save()
            response_data = {'message': 'Group membership created successfully'}
            return Response(response_data)
        except Exception as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=500)

    return Response({'error': 'Invalid request method'}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def replyComment(request):
    serializer = ReplyCommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Comment Posted"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)