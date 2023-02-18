from rest_framework import serializers
from .models import Person
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'
        #['Email', 'Password']
        #fields = ('id', 'first_name', 'last_name', 'email', 'password')

        #def create(self, validated_data):
        #    return Person.objects.create(validated_data)
        
        #def update(self, instance, validated_data):
        #    instance.Email = validated_data.get('Email', instance.Email)
        #    instance.Passwrod = validated_data.get('Password', instance.Password)
        #    instance.save()
        #    return instance

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

        @classmethod

        def get_token(cls, user):
            token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
            token['username'] = user.Username
            return token

