from django.urls import path
from suggestion.views import my_view

app_name = 'suggestion'
urlpatterns = [
    path('chatbot/', my_view, name='chatbot'),
]