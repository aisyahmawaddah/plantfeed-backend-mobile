from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Person

#from .models import Booking
# from .models import Comment
from .models import *

admin.site.register(Person)