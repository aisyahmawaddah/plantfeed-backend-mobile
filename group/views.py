from django.shortcuts import render
from django.http.response import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django import forms
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import IntegrityError
from .models import Group_tbl, GroupMembership, GroupPlantTagging, GroupSoilTagging, pl_graph_sharing, pl_graph_api
from .forms import GroupForm
from member.models import Person, SoilTag, PlantTag, Memberlist
from sharing.models import GFeedPlantTagging, GFeedSoilTagging, GroupTimeline, GroupTimelineComment, FeedPlantTagging, FeedSoilTagging
import json
from django.views.decorators.csrf import csrf_exempt

#group
def mainGroup(request):
    if request.method=='POST':
        person=Person.objects.get(Email=request.session['Email'])
        #Age = request.POST.get('Age')
        #soiltag=request.POST.get('soiltag')
        #soilTagID = SoilTag.objects.filter(SoilTagName=soiltag)
        #plantTagID = PlantTag.objects.filter(PlantTagName=planttag)
        #groupPlantTag=GroupPlantTagging.objects.filter(plantTag=plantTagID)
        #groupSoilTag=GroupSoilTagging.objects.filter(soilTag=soilTagID)

        #soiltag=SoilTag.objects.all()
        #planttag=PlantTag.objects.all()
        
        State = request.POST.get('State')
        #searchgp=Group_tbl.objects.all()
        searchgp=Group_tbl.objects.filter(State=State)
        return render(request,'MainPageGroup.html', {'person':person,'group':searchgp})
    
    try:
        
        person=Person.objects.get(Email=request.session['Email'])
        group=Group_tbl.objects.all()
        #soiltag=SoilTag.objects.all()
        #planttag=PlantTag.objects.all()
        groupMember=GroupMembership.objects.filter(GroupMember=person)
        searchgp=Group_tbl.objects.raw('select * from Group_tbl')
        fss =FileSystemStorage()
        uploaded_file = fss.url(group)
        return render(request,'MainPageGroup.html',{'group':group, 'uploaded_file':uploaded_file, 'person':person, 'groupMember':groupMember})

    except Group_tbl.DoesNotExist:
        raise Http404('Data does not exist')


def AddGroup(request):
    Username=Person.objects.get(Email=request.session['Email'])
    soilTagList=SoilTag.objects.all()
    plantTagList=PlantTag.objects.all()
    
    if request.method=='POST':
        Name=request.POST.get('Name')
        About=request.POST.get('About')
        Media = request.FILES['Photo']
        Age = request.POST.get('Age')
        State = request.POST.get('State')
        fss =FileSystemStorage()
        file = fss.save(Media.name, Media)

        groupID = Group_tbl(Name=Name,About=About,Media=Media,Age=Age,State=State,Username=Username).save()
        group = Group_tbl.objects.get(id=groupID)

        soilTagsID = request.POST.getlist('SoilTag')
        plantTagsID = request.POST.getlist('PlantTag')

        for soilTagsID in soilTagsID:
            soilTag = SoilTag.objects.get(id=soilTagsID)
            GroupSoilTagging(GroupSoilTag = group, soilTag=soilTag).save()

        for plantTagsID in plantTagsID:
            plantTag = PlantTag.objects.get(id=plantTagsID)
            GroupPlantTagging(GroupPlantTag = group, plantTag=plantTag).save()

        messages.success(request,'The new group ' + request.POST['Name'] + " is create succesfully..!")
        
        return redirect('group:JoinGroup', groupID)
    else :
        return render(request,'AddNewGroup.html', {'SoilTag':soilTagList, 'PlantTag':plantTagList})

def myGroup(request):
    try:
        Username=Person.objects.get(Email=request.session['Email'])
        # ambil group yg user create
        group=Group_tbl.objects.filter(Username=Username)
        # ambil group yg user join
        groupMembership=GroupMembership.objects.filter(GroupMember=Username)
        return render(request,'MyGroup.html',{'group':group,'groupMembership':groupMembership})
    except Group_tbl.DoesNotExist:
        raise Http404('Data does not exist')

def viewGroup(request,pk):
    try:
        user=Person.objects.get(Email=request.session['Email'])
        group = Group_tbl.objects.get(id=pk)
        groupSharing = GroupTimeline.objects.filter(GroupFK=group)
        chartSharing = pl_graph_sharing.objects.filter(Group_fk=group)
        groupComment = GroupTimelineComment.objects.all()
        groupMembership=GroupMembership.objects.filter(GroupName=group)
        memberList = Memberlist.objects.all().filter(to_person=user,from_person=user)
        #memberList2 = Memberlist.objects.all().filter(to_person=user)
        return render(request,'ViewGroup.html',{'group':group,'groupMembership':groupMembership, 'memberList':memberList, 'groupSharing':groupSharing, 'user':user, 'groupComment':groupComment, 'chartSharing':chartSharing})
    except Group_tbl.DoesNotExist:
        raise Http404('Data does not exist')

# cuba
def showGroup(request):

    lastGroup = Group_tbl.objects.last()

    Media = lastGroup.Media
    
    form = GroupForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()

    context={'Media':Media,
            'form':form
            }

    return render(request,'group.html',context)



def joinGroup(request, pk):
    try:
        group = Group_tbl.objects.get(id=pk)
        user=Person.objects.get(Email=request.session['Email'])
        userName = user.Name
        groupName = group.Name
        GroupMembership(GroupName=group, GroupMember=user).save()
        messages.success(request,'The joining of ' + userName + ' in group ' + groupName + ' is succesful..!')
        # return render(request,'MainGroup.html', {'group':group, 'uploaded_file':uploaded_file, 'person':person})
        return redirect('group:MainGroup')
    except Group_tbl.DoesNotExist:
        raise Http404('Data does not exist')

    except IntegrityError:
        messages.error(request,'You already joined group ' + groupName + '!')
        return redirect('group:MainGroup')


def deleteGroup(request, pk):
    
    try:
        group=Group_tbl.objects.get(id=pk)
        group2=Group_tbl.objects.get(id=pk)
        
        data=Group_tbl.objects.all()
        if request.method=='POST':
            group.deleteRecordIgrow()
            group2.deleteRecordFarming()
            messages.success(request,'The ' + group.Name + " is deleted succesfully..!")
            return redirect('group:MyGroup')
        
        else:
            return render(request, 'deleteGroup.html', {'group':group})
        
    except Group_tbl.DoesNotExist:
        messages.success(request,'No record of the workshop!')
        return redirect('group:MyGroup')


def updateGroup(request, pk):
    try:
        group=Group_tbl.objects.get(id=pk)
        # group_farming = Group_tbl.objects.get(id=pk)
        soilTag=GroupSoilTagging.objects.filter(GroupSoilTag=group)
        plantTag=GroupPlantTagging.objects.filter(GroupPlantTag=group)
        
        soilTag=GroupSoilTagging.objects.filter(GroupSoilTag=group)
        soilTagList=SoilTag.objects.all()

        plantTag=GroupPlantTagging.objects.filter(GroupPlantTag=group)
        plantTagList=PlantTag.objects.all()

        if request.method=='POST':
            group.Name=request.POST.get('Name')
            group.About=request.POST.get('About')
            group.Media = request.FILES['Photo']
            group.Age = request.POST.get('Age')
            group.State=request.POST.get('State')
            fss = FileSystemStorage()
                    
            currentSoilTag=GroupSoilTagging.objects.filter(GroupSoilTag=group)
            farmingSoilTag2=GroupSoilTagging.objects.filter(GroupSoilTag=group)

            currentPlantTag=GroupPlantTagging.objects.filter(GroupPlantTag=group)
            farmingPlantTag2=GroupPlantTagging.objects.filter(GroupPlantTag=group)

        
            newSoilTags = request.POST.getlist('SoilTag')
            newPlantTags = request.POST.getlist('PlantTag')

            try:
                if soilTag:
                    for currentSoilTag in currentSoilTag:
                        currentSoilTag.deleteRecordFarming()
                    for farmingSoilTag2 in farmingSoilTag2:
                        farmingSoilTag2.deleteRecordIgrow()

                for newSoilTag in newSoilTags:
                    new_soilTag = SoilTag.objects.get(id=newSoilTag)
                    GroupSoilTagging(GroupSoilTag=group, soilTag = new_soilTag).save()

                
                if plantTag:
                    for currentPlantTag in currentPlantTag:
                        currentPlantTag.deleteRecordFarming()
                    for farmingPlantTag2 in farmingPlantTag2:
                        farmingPlantTag2.deleteRecordIgrow()

                for newPlantTag in newPlantTags:
                    new_plantTag = PlantTag.objects.get(id=newPlantTag)
                    GroupPlantTagging(GroupPlantTag = group, plantTag=new_plantTag).save()


            except IntegrityError:
                messages.error(request,'The group is already been tagged with the chosen tag(s)!')
            
            group.save()

            messages.success(request,'The ' + request.POST['Name'] + " is updated succesfully..!")
            # return render(request,'MyGroup.html')
            return redirect('group:MyGroup')
        else :
            return render(request,'UpdateGroup.html', {'data':group, 'SoilTag':soilTagList, 'currentSoilTag':soilTag, 'PlantTag':plantTagList, 'currentPlantTag':plantTag})
    
    except Group_tbl.DoesNotExist:
            raise Http404('Data does not exist')


def Group_SoilTag(request):

    person=Person.objects.get(Email=request.session['Email'])
    group=Group_tbl.objects.all()
    fss =FileSystemStorage()
    uploaded_file = fss.url(group)
        

    if request.method=='POST':
        
        soilTagsID = request.POST.get('SoilTag')
        soilTagging = SoilTag.objects.get(id=soilTagsID)

        filteredGroup = GroupSoilTagging.objects.filter(soilTag=soilTagging)
        # filteredGroup = filtered_Soiltag.filter(GroupSoilTag__in=feed)

        return render(request,'SoilFilteredGroup.html', {'filteredGroup':filteredGroup, 'chosen_soilTag':soilTagging, 'ori_group':group})

    else:

        context = {
            'SoilTags': SoilTag.objects.all(), 
        }

        # return render(request, 'MainGroup.html', {'data':groupData, 'context_SoilTags':context})   
        return render(request,'MainPageGroup.html',{'group':group, 'uploaded_file':uploaded_file, 'person':person, 'context_SoilTags':context}) 


def Group_PlantTag(request):

    person=Person.objects.get(Email=request.session['Email'])
    group=Group_tbl.objects.all()
    fss =FileSystemStorage()
    uploaded_file = fss.url(group)

    if request.method=='POST':
        
        plantTagsID = request.POST.get('PlantTag')
        plantTagging = PlantTag.objects.get(id=plantTagsID)

        filteredGroup = GroupPlantTagging.objects.filter(plantTag=plantTagging)

        return render(request,'PlantFilteredGroup.html', {'filteredGroup':filteredGroup, 'chosen_plantTag':plantTagging, 'ori_group':group})

    else:

        context = {
            'PlantTags' : PlantTag.objects.all(),
        }
        
        return render(request,'MainPageGroup.html',{'group':group, 'uploaded_file':uploaded_file, 'person':person, 'context_PlantTags':context}) 

def PLSharing(request, pk):
    
    user=Person.objects.get(Email=request.session['Email'])
    group = Group_tbl.objects.get(id=pk)   
    user_charts = pl_graph_api.objects.filter(Person_fk=user)

    if request.method == "POST":
        selected_id = request.POST.get('chart')
        
        # Ensure selected_id is a string and handle custom link case
        if selected_id == 'Others':
            plGraph = pl_graph_sharing()
            plGraph.title = request.POST.get('title')
            
            if len(plGraph.title) > 100:
                messages.error(request, 'Sharing title name cannot be more than 100 characters.')
                return redirect(request.META.get('HTTP_REFERER'))
            
            plGraph.description = request.POST.get('description')
            if len(plGraph.description) > 500:
                messages.error(request, 'Sharing description name cannot be more than 500 characters.')
                return redirect(request.META.get('HTTP_REFERER'))
            
            plGraph.link = request.POST.get('customLink')
            plGraph.Group_fk = group
            plGraph.Person_fk = user
            
            plGraph.save()
        elif selected_id.isdigit():
            graph = get_object_or_404(pl_graph_api, id=selected_id)
            plGraph = pl_graph_sharing()
            plGraph.title = request.POST.get('title')
            
            if len(plGraph.title) > 100:
                messages.error(request, 'Sharing title name cannot be more than 100 characters.')
                return redirect(request.META.get('HTTP_REFERER'))
            
            plGraph.description = request.POST.get('description')
            if len(plGraph.description) > 500:
                messages.error(request, 'Sharing description name cannot be more than 500 characters.')
                return redirect(request.META.get('HTTP_REFERER'))
            
            plGraph.link = graph.embed_link
            plGraph.chart_type = graph.chart_type
            plGraph.Group_fk = group
            plGraph.Person_fk = user
            
            plGraph.save()
        else:
            messages.error(request, 'Invalid selection.')
            return redirect(request.META.get('HTTP_REFERER'))
        
        return redirect('group:ViewGroup', pk)
    else :
        return render(request,'AddPLSharing.html', {'charts':user_charts})

@csrf_exempt
def PLGraphAPI(request):
    if request.method == "POST":
        try:
            graph = pl_graph_api()
            data = json.loads(request.body)
            userid = data.get('userid')
            user = get_object_or_404(Person, id=userid)
            graph.name = data.get('chart_name')
            graph.embed_link = data.get('embed_link')
            graph.chart_type = data.get('chart_type')
            graph.start_date = data.get('start_date')
            graph.end_date = data.get('end_date')
            graph.Person_fk = user
            
            graph.save()     
            
            return JsonResponse({'success': 'Chart has been saved'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'No data detected'}, status=404)

def AddGroupSharing(request, pk):
    
    user=Person.objects.get(Email=request.session['Email'])
    group = Group_tbl.objects.get(id=pk)
    groupSharing = GroupTimeline.objects.filter(GroupFK=group)
    
    groupMembership=GroupMembership.objects.filter(GroupName=group)
    memberList = Memberlist.objects.all().filter(to_person=user,from_person=user)
    #memberList2 = Memberlist.objects.all().filter(to_person=user)    
    soilTagList=SoilTag.objects.all()
    plantTagList=PlantTag.objects.all()

    if request.method=='POST':
        taggingSoil=SoilTag.objects.all()
        GroupTitle=request.POST.get('Title')
        GroupMessage=request.POST.get('Message')
        GroupSkill=request.POST.get('Skill')
        GroupState=request.POST.get('State')
        # Photo=request.FILES['Photo']
        # Video=request.FILES['Video']
        GroupPhoto=request.FILES.get('Photo',None)
        #GroupVideo=request.FILES.get('Video', None)
        fss =FileSystemStorage()
        
        Gfeed_id = GroupTimeline(GroupTitle=GroupTitle,GroupMessage=GroupMessage,GroupPhoto=GroupPhoto,GroupFK=group,CreatorFK=user,GroupSkill=GroupSkill,GroupState=GroupState).save()
        Gfeed = GroupTimeline.objects.get(id=Gfeed_id)
        groupComment = GroupTimelineComment.objects.filter(GrpFeedFK=Gfeed)
        soilTagsID = request.POST.getlist('SoilTag')
        plantTagsID = request.POST.getlist('PlantTag')

        for soilTagsID in soilTagsID:
            soilTag = SoilTag.objects.get(id=soilTagsID)
            GFeedSoilTagging(FeedSoilTag = Gfeed, soilTag=soilTag).save()

        for plantTagsID in plantTagsID:
            plantTag = PlantTag.objects.get(id=plantTagsID)
            GFeedPlantTagging(FeedPlantTag = Gfeed, plantTag=plantTag).save()

        messages.success(request,'The new feed is save succesfully..!')
        return render(request,'ViewGroup.html',{'group':group,'groupMembership':groupMembership, 'memberList':memberList, 'groupSharing':groupSharing, 'user':user, 'groupComment':groupComment})


    else :
        # taggingSoil=SoilTag.objects.all()
        return render(request,'AddGroupSharing.html', {'SoilTag':soilTagList, 'PlantTag':plantTagList})

def addGSComment(request, pk):
    commenter=Person.objects.get(Email=request.session['Email'])
    groupFeed = GroupTimeline.objects.get(id=pk)
    allfeed = GroupTimeline.objects.all()
    comment = GroupTimelineComment.objects.all()
    #likes = Likes.objects.all()
    #group_id = feed.Group.id
    
    if request.method=='POST':
        
        Message=request.POST.get('Message')
        Picture=request.FILES.get('Pictures',None)
        #Video=request.FILES.get('Video',None)
        fss =FileSystemStorage()
        
        GroupTimelineComment(GrpMessage=Message,GrpPictures=Picture,GrpFeedFK=groupFeed,GrpCommenterFK=commenter).save(),
        # messages.success(request,'The comment is save succesfully..!')
        # return render(request,'addComment.html')
        #return redirect('sharing:Forum', group_id)
        #return redirect(request, 'MainPageSharing.html',{'feed':feed, 'allfeed':allfeed, 'commenter':commenter, 'comment':comment, 'likes':likes})
        return redirect('group:MainGroup')
    else :
        return render(request,'MainPageGroup.html', {'feed':groupFeed, 'allfeed':allfeed})   

