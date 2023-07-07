from django.shortcuts import render
from .models import ChatBot

def my_view(request):
    if request.method == 'POST':
        selected_choice = request.POST.get('choice')
        choices = ChatBot.objects.all()
        choice = ChatBot.objects.get(Question=selected_choice)
        question = choice.Question
        answer = choice.Answer
        return render(request, 'chatbot.html', {'question': question, 'answer':answer, 'choices':choices})
    
    choices = ChatBot.objects.all()
    return render(request, 'chatbot.html', {'choices': choices})
