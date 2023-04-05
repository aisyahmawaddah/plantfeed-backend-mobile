from rest_framework import serializers
from .models import Person
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.authtoken.models import Token

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

