from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.http.response import Http404
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib import messages
from .models import Person, Memberlist, MemberRequest, Room, Message
from django.contrib import auth
from plantfeed import encryption_util
from django.core.files.storage import FileSystemStorage
from django.db import IntegrityError


def index(request):
  template = loader.get_template('index.html')
  return HttpResponse(template.render())

def UserReg(request):
    if request.method=='POST':
        Email = request.POST.get('email')
        Password = request.POST.get('password')
        Username=request.POST.get('username')
        Name=request.POST.get('name')
        DateOfBirth=request.POST.get('dob')
        Age=request.POST.get('age')
        District=request.POST.get('district')
        State=request.POST.get('state')
        Occupation=request.POST.get('occupation')
        About=request.POST.get('about')
        Gender=request.POST.get('gender')
        MaritalStatus=request.POST.get('maritalstatus')
        UserLevel = request.POST.get('userlevel')
        #Photo = request.POST.get('Photo')
        Photo=request.FILES['Photo']
        Person(Email=Email,Password=Password,Username=Username,Name=Name,DateOfBirth=DateOfBirth,Age=Age,District=District,State=State,
            Occupation=Occupation,About=About,Gender=Gender,MaritalStatus=MaritalStatus,UserLevel=UserLevel,Photo=Photo).save(),

        messages.success(request,'The new user ' + Username + " is save succesfully..!")
        return render(request,'registration.html')
    else :
        return render(request,'registration.html')

    
    #user login
def login(request):
    if request.method == "POST":
        try:
            Userdetails = Person.objects.get(Email = request.POST['Email'], Password = (request.POST['Pwd']))
            UserLevel = (request.POST.get('UserLevel'))
            print("Username", Userdetails)
            request.session['Email'] = Userdetails.Email
            person = Person.objects.filter(Email = request.POST['Email'])
            request.session['UserLevel'] = Userdetails.UserLevel
            if request.session['UserLevel'] == 'user':
                return render(request,'homepage.html',{'person' : person})
            else:
                return render(request,'homepageAdmin.html',{'person' : person})
        except Person.DoesNotExist as e:
            messages.success(request,'Username/Password Invalid..!')
    return render(request,'login.html')

#homepage for user
def homepage(request):
    person = Person.objects.filter(Email=request.session['Email'])
    
    return render(request, 'homepage.html',{'person': person })

#homepage for admin
def homepageAdmin(request):
    person = Person.objects.filter(Email=request.session['Email'])

    return render(request, 'homepageAdmin.html',{'person': person })

#logout
def logout(request):
    try:
        del request.session['Email']
    except:
        return render(request,'index.html')
    return render(request,'index.html')

#profile edit button
def Profile(request):
    person = Person.objects.filter(Email=request.session['Email'])
    return render(request, 'profile2.html',{'person': person })
    

#profile edit form
def EditProfile(request):
    person = Person.objects.filter(Email=request.session['Email'])
    #p = Person.objects.get(pk=fk1)
    if request.method=='POST':
        t = Person.objects.get(Email=request.session['Email'])
        t.Password=request.POST['Password']
        t.Username=request.POST.get('Username')
        t.Name=request.POST.get('Name')
        t.DateOfBirth=request.POST.get('DateOfBirth')
        t.Age=request.POST['Age']
        t.District=request.POST['District']
        t.State=request.POST['State']
        t.Occupation=request.POST['Occupation']
        t.About=request.POST['About']
        t.Gender=request.POST.get('Gender')
        t.MaritalStatus=request.POST.get('MaritalStatus')
        #t.Photo=request.POST.get('photo')
        t.Photo=request.FILES['Photo']
        # Video=request.FILES['Video']
        #Photo=request.FILES.get('Photo',None)
        #Video=request.FILES.get('Video', None)
        fss =FileSystemStorage()
        file = fss.save(t.Photo.name, t.Photo)
        t.save()
        return render(request,'profile2.html',{'person': person})
    else:
        #decryptPass = encryption_util.decrypt(person.Password)
        return render(request, 'editProfileForm2.html',{'person': person})
       
def MainMember(request):
    
    user=Person.objects.get(Email=request.session['Email'])

    
    try:
        userRequestList = MemberRequest.objects.all().filter(to_user=user)
        memberList = Memberlist.objects.all().filter(to_person=user) 
        
        return render(request, 'MemberMainPage.html',{'userRequestList':userRequestList, 'memberList':memberList })
    
    except:
        return render(request, 'MemberMainPage.html')

def SearchMember(request):

    user=Person.objects.get(Email=request.session['Email'])

    if request.method == 'GET':
        userRequestList = MemberRequest.objects.all().filter(to_user=user)
        memberList = Memberlist.objects.all().filter(to_person=user)
        search = request.GET.get('search')
        Name = Person.objects.all().filter(Name=search)
        # cuba
        Name2 = Name.exclude(Email=request.session['Email'])
        return render(request, 'MemberMainPage.html', {'Name': Name2,'userRequestList':userRequestList, 'memberList':memberList})

def sendMemberRequest(request, userID):
    
    try:
        from_user=Person.objects.get(Email=request.session['Email'])
        to_user=Person.objects.get(id=userID)
        to_user_id = to_user.id
        
        MemberRequest(from_user=from_user, to_user=to_user).save()
        messages.success(request,'Member request to ' + to_user.Name + " is sent succesfully..!")

        return redirect('v2MainSearchbar',to_user_id)

    except MemberRequest.DoesNotExist:
        raise Http404('Data does not exist')

    except IntegrityError:
        messages.error(request,'You already sent friend request to ' + to_user.Name + '!')
        return redirect('v2MainSearchbar',to_user_id)

def v2MainSearchbar(request, pk):
    user=Person.objects.get(Email=request.session['Email'])
    person = Person.objects.get(id=pk)
    userRequestList = MemberRequest.objects.all().filter(to_user=user)
    memberList = Memberlist.objects.all().filter(to_person=user)
    #return render(request, 'MemberMainPage.html', {'sentRequestUser': person,'userRequestList':userRequestList, 'memberList':memberList})
    return redirect('MemberMainPage')

def acceptMemberRequest(request, requestID):
    user=Person.objects.get(Email=request.session['Email'])
    
    member_request = MemberRequest.objects.get(id=requestID)
    member_request2 = MemberRequest.objects.get(id=requestID)

    from_person = member_request.from_user
    room_id = Room(member1 = user, member2 = from_person).save()
    room = Room.objects.get(id=room_id)

    try:

        if member_request.to_user == user:
            
            
            Memberlist(from_person=from_person, to_person=user, chatRoom=room).save()
            Memberlist(from_person=user, to_person=from_person, chatRoom=room).save()
            
            member_request.deleteRecordIgrow()
            #member_request2.deleteRecordFarming()
            
            messages.success(request,'Member request accepted ')
            return redirect('MemberMainPage')
            
        else:
            messages.success(request,'Member request does not accepted ')
            return redirect('MemberMainPage')
    
    except IntegrityError:
        messages.error(request,'You already membered with ' + from_person.Name + '!')
        return redirect('MainMember')

def chatRoom(request, room):

    room = Room.objects.get(id = room)
    user=Person.objects.get(Email=request.session['Email'])

    return render(request, 'ChatRoom.html', {'room':room, 'user':user})

def send(request):
    message = request.POST['message']
    user = request.POST['sender']
    room_id = request.POST['room']
    room = Room.objects.get(id = room_id)
    # user = Person.objects.get(id = user_id)


    Message(value=message, sender=user, room=room).save()
    
    return HttpResponse('Message sent successfully')

def getMessages(request, room):
    room = Room.objects.get(id=room)

    messages = Message.objects.filter(room=room.id)
    return JsonResponse({"messages":list(messages.values())})




