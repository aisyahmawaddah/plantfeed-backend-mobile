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

class UserAuthentication(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get(user=user)
        return Response(token.key)

class UserList(APIView):

    def get(self, request):
        model =Person.objects.all()
        serializer = UsersSerializer(model, many=True)
        return Response(serializer.data)
        
    def post(self, request):
        serializer = UsersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateProfileView(generics.UpdateAPIView):

    queryset = Person.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UpdateProfileSerializer

#Login
@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    body = json.loads(request.body)
    email = body['email'] 
    password = body['password']

    try:
        Account = Person.objects.get(Email=email, password=password)
        token = Token.objects.get_or_create(user=Account)[0].key
        user = Token.objects.get(key=token).user
        print(user.Name)
        Res = {
            "Email": Account.Email,
            "Password": Account.password,
            "ID":Account.id,
            "token": token
            
        }
        return Response(Res)
    except BaseException as e:
         return Response({'message': 'Incorect Email or Password'})
        #raise ValidationError({"400": f'{str(e)}'})

#Get user from token
@api_view(['GET'])
@permission_classes([AllowAny])
def getUserFromToken(request, pk):
    user = Token.objects.get(key=pk).user
    serializer = UsersSerializer(user, many=False)
    return Response(serializer.data)


#@api_view(['POST'])
#@permission_classes([AllowAny])
#def postFeed(request):
    """
    Create a new post.
    """
#    serializer = FeedSerializer(data=request.data)
#    if serializer.is_valid():
#        serializer.save()
#        return Response({"message": "Feed Posted"}, status=status.HTTP_201_CREATED)
#    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#class CreatorFeedView(APIView):
#    permission_classes = [AllowAny]
#    def get(self, request, creator_id):
#        feeds = Feed.objects.filter(Creator_id=creator_id).order_by('-created_at')
#        serializer = FeedSerializer(feeds, many=True)
#        return Response(serializer.data, status=status.HTTP_200_OK)
    
#class DeleteFeedView(APIView):
#    permission_classes = [AllowAny]
#    def post(self, request):
#        feed_id = request.data.get('id')
#        try:
#            feed = Feed.objects.get(id=feed_id)
#            feed.delete()
#            return Response({'message': 'Feed deleted successfully.'}, status=status.HTTP_200_OK)
#        except Feed.DoesNotExist:
#            return Response({'message': 'Feed not found.'}, status=status.HTTP_404_NOT_FOUND)
#        except Exception as e:
#            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateProfileView(generics.UpdateAPIView):

    queryset = Person.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UpdateProfileSerializer