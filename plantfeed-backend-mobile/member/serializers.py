from rest_framework import serializers
from .models import Person
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from .models import Person

class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        #fields = ['Email', 'Password']
        fields = '__all__'

    def validate(self, data):
        username = data.get("username", None)
        password = data.get("password", None)
        if Person.objects.filter(username=username).filter(password=password).first():
            return True

        raise NotAuthenticated

    
        
        #def update(self, instance, validated_data):
        #    instance.Email = validated_data.get('Email', instance.Email)
        #    instance.Passwrod = validated_data.get('Password', instance.Password)
        #    instance.save()
        #    return instance

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields= ('password','Name', 'Age', 'Username','DateOfBirth','District','State','Occupation','About','Gender','MaritalStatus')

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

        instance.password = validated_data['password']
        instance.Name = validated_data['Name']
        instance.Age = validated_data['Age']
        instance.Username = validated_data['Username']
        instance.DateOfBirth = validated_data['DateOfBirth']
        instance.District = validated_data['District']
        instance.State = validated_data['State']
        instance.Occupation = validated_data['Occupation']
        instance.About = validated_data['Abour']
        instance.Gender = validated_data['Gender']
        instance.MaritalStatus = validated_data['MaritalStatus']

        instance.save()

        return instance
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

        @classmethod

        def get_token(cls, user):
            token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
            token['username'] = user.username
            return token

#class FeedSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Feed
#        fields = ['id', 'Title', 'Message', 'Creator_id', 'created_at' ,'Photo']

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
#    Photo = PhotoField(allow_null=True, required=False, upload_to='media/uploads/profile')

    class Meta:
        model = Person
        fields = ('Name', 'Age', 'Username',  'State', 'District', 'Photo')

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