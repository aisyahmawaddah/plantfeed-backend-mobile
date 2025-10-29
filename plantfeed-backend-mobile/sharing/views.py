from django.shortcuts import render
from django.http.response import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
# from LOGIN.models import Person as FarmingPerson
# from LOGIN.models import Feed, Booking, Workshop, Group_tbl, Member 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
# from .forms import CreateInDiscussion, PersonForm, UserUpdateForm
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Feed, Comment, GroupTimeline, GroupTimelineComment,Likes
from group.models import Group_tbl, GroupMembership
from member.models import Person, SoilTag, PlantTag, Memberlist
from sharing.models import FeedSoilTagging, FeedPlantTagging
from group.views import viewGroup

# Create your views here.


#sharing
def mainSharing(request):
    try:
        feed=Feed.objects.all()
        user=Person.objects.get(Email=request.session['Email'])
        user_group = GroupMembership.objects.filter(GroupMember_id=user)
        comment = Comment.objects.all()
        likes = Likes.objects.all()
        memberList = Memberlist.objects.all().filter(to_person=user)

        soilTags = SoilTag.objects.all()
        fss =FileSystemStorage()
        
        return render(request,'MainPageSharing.html',{'allfeed':feed ,'soilTags':soilTags, 'user_group':user_group, 'comment':comment, 'likes':likes, 'memberList':memberList})
    except Feed.DoesNotExist:
        raise Http404('Data does not exist')

def AddSharing(request):
    
    #group_forum = Group_tbl.objects.get(id=pk)
    creator=Person.objects.get(Email=request.session['Email'])
    soilTagList=SoilTag.objects.all()
    plantTagList=PlantTag.objects.all()

    if request.method=='POST':
        taggingSoil=SoilTag.objects.all()
        Title=request.POST.get('Title')
        Message=request.POST.get('Message')
        Skill=request.POST.get('Skill')
        State=request.POST.get('State')
        Photo=request.FILES['Photo']
        # Video=request.FILES['Video']
        #Photo=request.FILES.get('Photo',None)
        #Video=request.FILES.get('Video', None)
        
        
        feed_id = Feed(Title=Title,Message=Message,Photo=Photo,Creator=creator,Skill=Skill,State=State).save()
        feed = Feed.objects.get(id=feed_id)
        allfeed = Feed.objects.all()

        soilTagsID = request.POST.getlist('SoilTag')
        plantTagsID = request.POST.getlist('PlantTag')

        for soilTagsID in soilTagsID:
            soilTag = SoilTag.objects.get(id=soilTagsID)
            FeedSoilTagging(FeedSoilTag = feed, soilTag=soilTag).save()

        for plantTagsID in plantTagsID:
            plantTag = PlantTag.objects.get(id=plantTagsID)
            FeedPlantTagging(FeedPlantTag = feed, plantTag=plantTag).save()

        messages.success(request,'The new feed is save succesfully..!')
        #return render(request,'MainPageSharing.html', {'feed':feed, 'allfeed':allfeed, 'creator':creator})
        return redirect('sharing:MainSharing')
    else :
        # taggingSoil=SoilTag.objects.all()
        return render(request,'AddNewSharing.html', {'SoilTag':soilTagList, 'PlantTag':plantTagList})



  

def updateSharing(request, pk):
    # feed = Feed.objects.filter(id=pk)
    feed = Feed.objects.get(id=pk)
    soilTag=FeedSoilTagging.objects.filter(FeedSoilTag=feed)
    farming_soilTag=FeedSoilTagging.objects.filter(FeedSoilTag=feed)
    soilTagList=SoilTag.objects.all()
    plantTag=FeedPlantTagging.objects.filter(FeedPlantTag=feed)
    plantTagList=PlantTag.objects.all()
    
    if request.method=='POST':
        feed.Title=request.POST['Title']
        feed.Message=request.POST.get('Message')
        feed.State=request.POST.get('State')
        feed.Skill=request.POST.get('Skill')
        feed.Photo=request.FILES.get('Photo',None)
        #feed.Video=request.FILES.get('Video', None)
        fss =FileSystemStorage()

        newSoilTags = request.POST.getlist('SoilTag')
        newPlantTags = request.POST.getlist('PlantTag')

        currentSoilTag=FeedSoilTagging.objects.filter(FeedSoilTag=feed)
        farmingSoilTag2=FeedSoilTagging.objects.filter(FeedSoilTag=feed)
        currentPlantTag=FeedPlantTagging.objects.filter(FeedPlantTag=feed)
        farmingPlantTag2=FeedPlantTagging.objects.filter(FeedPlantTag=feed)
        

        if soilTag:    
            for farmingSoilTag2 in farmingSoilTag2:
                farmingSoilTag2.deleteRecordIgrow()

        for newSoilTag in newSoilTags:
            new_soilTag = SoilTag.objects.get(id=newSoilTag)
            FeedSoilTagging(FeedSoilTag = feed, soilTag=new_soilTag).save()

        if plantTag:
            for farmingPlantTag2 in farmingPlantTag2:
                farmingPlantTag2.deleteRecordIgrow()

        for newPlantTag in newPlantTags:
            new_plantTag = PlantTag.objects.get(id=newPlantTag)
            FeedPlantTagging(FeedPlantTag = feed, plantTag=new_plantTag).save()

        feed.save()

        messages.success(request,'The post of ' + request.POST['Title'] + " is updated succesfully..!")
        return redirect('../MainSharing')
    else:
        return render(request, 'UpdateSharing.html', {'feed': feed, 'SoilTag':soilTagList, 'currentSoilTag':soilTag, 'PlantTag':plantTagList, 'currentPlantTag':plantTag})


def deleteSharing(request,pk):
    try:
        feed=Feed.objects.get(id=pk)
        #feed2=Feed.objects.get(id=pk)

        data=Feed.objects.all()
        
        feed.deleteRecordIgrow()
            #feed2.deleteRecordFarming()
            # messages.success(request,'The ' + feed.Title + " is deleted succesfully..!")
        return redirect('../MainSharing')
        
        
    except Feed.DoesNotExist:
        messages.success(request,'No record of the feed!')
        return redirect('../MainSharing')

def AddLikes(request,pk):
    try:
        feed=Feed.objects.get(id=pk)
        liker=Person.objects.get(Email=request.session['Email'])
        
        #feed2=Feed.objects.get(id=pk)

        data=Feed.objects.all()
        
        Likes(Feed=feed,Liker=liker).save(),

            #feed2.deleteRecordFarming()
            # messages.success(request,'The ' + feed.Title + " is deleted succesfully..!")
        return redirect('../MainSharing')
        
        
    except Feed.DoesNotExist:
        messages.success(request,'No record of the feed!')
        return redirect('../MainSharing')


def viewForum(request, pk):
    if request.method=="POST":
        data = Group_tbl.objects.get(id=pk)
        Skill=request.POST.get('Skill')
        State=request.POST.get('State')
        # soilTags = FeedSoilTagging.objects.all()
        feed = Feed.objects.filter(Group = data)
        searchshare=Feed.objects.raw('select * from Feed where Skill="'+Skill+'" and State="'+State+'"')
        return render(request, 'Forum.html', {'feed': feed, 'data':data,'feed':searchshare})
    try:
            data = Group_tbl.objects.get(id=pk)
            feed = Feed.objects.filter(Group = data)
            return render(request,'Forum.html', {'feed':feed,'data':data})
    except Feed.DoesNotExist:
            raise Http404('Data does not exist') 

#def addLikes(request, pk):
#    liker=Person.objects.get(Email=request.session['Email'])
##    feed = Feed.objects.get(id=pk)
#    allfeed = Feed.objects.all()
#    likes = Likes.objects.all()
#    comment = Comment.objects.all()
    #group_id = feed.Group.id
    
#    if request.method=='POST':
        #like = request.POST.get('likes')
        #fss =FileSystemStorage()
        
#        Likes(Feed=feed,Liker=liker).save(),
       
#        return render(request, 'MainPageSharing.html',{'feed':feed, 'allfeed':allfeed, 'liker':liker, 'likes':likes, 'comment':comment})
#    else :
#        return render(request,'MainPageSharing.html', {'feed':feed, 'allfeed':allfeed})

def addComment(request, pk):
    commenter=Person.objects.get(Email=request.session['Email'])
    feed = Feed.objects.get(id=pk)
    allfeed = Feed.objects.all()
    comment = Comment.objects.all()
    likes = Likes.objects.all()
    #group_id = feed.Group.id
    
    if request.method=='POST':
        
        Message=request.POST.get('Message')
        Picture=request.FILES.get('Pictures',None)
        #Video=request.FILES.get('Video',None)
        fss =FileSystemStorage()
        
        Comment(Message=Message,Pictures=Picture,Commenter=commenter,Feed=feed).save(),
        # messages.success(request,'The comment is save succesfully..!')
        # return render(request,'addComment.html')
        #return redirect('sharing:Forum', group_id)
        #return redirect(request, 'MainPageSharing.html',{'feed':feed, 'allfeed':allfeed, 'commenter':commenter, 'comment':comment, 'likes':likes})
        return redirect('sharing:MainSharing')
    else :
        return render(request,'MainPageSharing.html', {'feed':feed, 'allfeed':allfeed})


def updateComment(request, pk):
   
    comment = Comment.objects.get(id=pk)
    group_id=comment.Feed.Group.id
    feed = comment.Feed
    if request.method=='POST':
       
       comment.Message=request.POST.get('Message')
       comment.Photo=request.FILES.get('Picture',None)
       #comment.Video=request.FILES.get('Video',None)
       fss =FileSystemStorage()
       comment.save()
    #    messages.success(request,"The comment of is updated succesfully..!")
       return redirect('../MainSharing')
    else:
        return render(request, 'MainPageSharing.html', {'comment': comment})

def deleteComment(request,pk):
    comment = Comment.objects.get(id=pk)
    #group_id=comment.Feed.Group.id
    #feed = comment.Feed
    try:
        comment=Comment.objects.get(id=pk)
        #comment2=Comment.objects.get(id=pk)

        
        comment.deleteRecordIgrow()
            #comment2.deleteRecordFarming()
            # messages.success(request,'The ' + feed.Title + " is deleted succesfully..!")
        return redirect('../MainSharing')
        
    except Comment.DoesNotExist:
        messages.success(request,'No record of the comment!')
        return redirect('../MainSharing')



def Sharing_SoilTag(request):

    person=Person.objects.get(Email=request.session['Email'])
    feed=Feed.objects.all()
    fss =FileSystemStorage()
    uploaded_file = fss.url(feed)
        

    if request.method=='POST':
        
        soilTagsID = request.POST.get('SoilTag')
        soilTagging = SoilTag.objects.get(id=soilTagsID)

        filteredSharing = FeedSoilTagging.objects.filter(soilTag=soilTagging)
        # filteredGroup = filtered_Soiltag.filter(GroupSoilTag__in=feed)

        return render(request,'SoilFilteredFeed.html', {'filteredSharing':filteredSharing, 'chosen_soilTag':soilTagging, 'ori_feed':feed})

    else:

        context = {
            'SoilTags': SoilTag.objects.all(), 
        }

        # return render(request, 'MainGroup.html', {'data':groupData, 'context_SoilTags':context})   
        return render(request,'MainPageSharing.html',{'feed':feed, 'uploaded_file':uploaded_file, 'person':person, 'context_SoilTags':context}) 


def Sharing_PlantTag(request):

    person=Person.objects.get(Email=request.session['Email'])
    feed=Feed.objects.all()
    fss =FileSystemStorage()
    uploaded_file = fss.url(feed)

    if request.method=='POST':
        
        plantTagsID = request.POST.get('PlantTag')
        plantTagging = PlantTag.objects.get(id=plantTagsID)

        filteredSharing = FeedPlantTagging.objects.filter(plantTag=plantTagging)

        return render(request,'PlantFilteredFeed.html', {'filteredSharing':filteredSharing, 'chosen_plantTag':plantTagging, 'ori_feed':feed})

    else:

        context = {
            'PlantTags' : PlantTag.objects.all(),
        }
        
        return render(request,'MainPageSharing.html',{'feed':feed, 'uploaded_file':uploaded_file, 'person':person, 'context_PlantTags':context}) 

