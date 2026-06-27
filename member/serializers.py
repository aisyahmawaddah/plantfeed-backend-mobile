from rest_framework import serializers
from .models import Person
from sharing.models import Feed
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.authtoken.models import Token


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = '__all__'

    def validate(self, data):
        username = data.get("username", None)
        password = data.get("password", None)
        if Person.objects.filter(username=username).filter(password=password).first():
            return True

        raise NotAuthenticated


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        token['username'] = user.username
        return token


class FeedSerializer(serializers.ModelSerializer):
    Creator_name = serializers.SerializerMethodField()
    Creator_photo = serializers.SerializerMethodField()
    Creator_username = serializers.SerializerMethodField()

    class Meta:
        model = Feed
        fields = ['id', 'Title', 'Message', 'Creator_id', 'Creator_name', 'created_at', 'Photo', 'Creator_photo', 'Creator_username']

    def get_Creator_name(self, feed):
        creator = Person.objects.get(id=feed.Creator_id)
        return creator.Name

    def get_Creator_photo(self, feed):
        creator = Person.objects.get(id=feed.Creator_id)
        return creator.Photo.url if creator.Photo else None

    def get_Creator_username(self, feed):
        creator = Person.objects.get(id=feed.Creator_id)
        return creator.Username


class PhotoField(serializers.ImageField):
    def init(self, args, **kwargs):
        self.upload_to = kwargs.pop('upload_to', '')
        super().init(args, **kwargs)

    def to_internal_value(self, data):
        if callable(self.upload_to):
            self.upload_to = self.upload_to(self.context['request'].user)
        self.upload_to = self.upload_to.strip('/')
        self.upload_to += '/'
        return super().to_internal_value(data)


class UpdateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = ('Name', 'Age', 'Username', 'State', 'District', 'Photo')

    def validate_email(self, value):
        user = self.context['request'].user
        if Person.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})
        return value

    def validate_username(self, value):
        user = self.context['request'].user
        if Person.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError({"username": "This username is already in use."})
        return value

    def update(self, instance, validated_data):
        instance.Name = validated_data.get('Name', instance.Name)
        instance.Age = validated_data.get('Age', instance.Age)
        instance.Username = validated_data.get('Username', instance.Username)
        instance.State = validated_data.get('State', instance.State)
        instance.District = validated_data.get('District', instance.District)
        instance.Photo = validated_data.get('Photo', instance.Photo)
        instance.save()
        return instance
