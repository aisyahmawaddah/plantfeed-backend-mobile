from workshop.models import Booking, Workshop
from rest_framework import serializers
from django.db import IntegrityError
class WorkshopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workshop
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    Poster = serializers.SerializerMethodField()
    Description = serializers.SerializerMethodField()
    StartTime = serializers.SerializerMethodField()
    Venue = serializers.SerializerMethodField()
    Speaker = serializers.SerializerMethodField()


    class Meta:
        model = Booking
        fields = ['id', 'ProgrammeName', 'Date', 'BookWorkshop_id', 'Participant_id', 'Messages', 'Poster', 'Description', 'StartTime', 'Venue', 'Speaker']

    def get_Poster(self, obj):
        if obj.BookWorkshop:
            workshop_serializer = WorkshopSerializer(obj.BookWorkshop)
            return workshop_serializer.data.get('Poster')
        return None
    
    def get_Description(self, obj):
        if obj.BookWorkshop:
            workshop_serializer = WorkshopSerializer(obj.BookWorkshop)
            return workshop_serializer.data.get('Description')
        return None
    
    def get_StartTime(self, obj):
        if obj.BookWorkshop:
            workshop_serializer = WorkshopSerializer(obj.BookWorkshop)
            return workshop_serializer.data.get('StartTime')
        return None
    def get_Venue(self, obj):
        if obj.BookWorkshop:
            workshop_serializer = WorkshopSerializer(obj.BookWorkshop)
            return workshop_serializer.data.get('Venue')
        return None
    
    def get_Speaker(self, obj):
        if obj.BookWorkshop:
            workshop_serializer = WorkshopSerializer(obj.BookWorkshop)
            return workshop_serializer.data.get('Speaker')
        return None
    

class WorkshopBookingCreateSerializer(serializers.ModelSerializer):
    BookWorkshop_id = serializers.IntegerField()
    Participant_id = serializers.IntegerField()

    class Meta:
        model = Booking
        fields = ['ProgrammeName', 'Date', 'BookWorkshop_id', 'Participant_id', 'Messages']

    def create(self, validated_data):
        book_workshop_id = validated_data.pop('BookWorkshop_id')
        participant_id = validated_data.pop('Participant_id')

        try:
            booking = Booking.objects.create(BookWorkshop_id=book_workshop_id, Participant_id=participant_id, **validated_data)
        except IntegrityError:
            raise serializers.ValidationError("Already booked")

        return booking
    
class CancelBookingSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def validate_id(self, value):
        try:
            booking = Booking.objects.get(id=value)
        except Booking.DoesNotExist:
            raise serializers.ValidationError('Booking not found.')
        return value