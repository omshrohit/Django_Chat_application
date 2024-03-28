from django.shortcuts import render,redirect
from  .models import Room,Topic,Message
from .forms import RoomForm
# for search
from django.db.models import Q
from   django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm



# Create your views here.

from django.http import HttpResponse



def home(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    rooms=Room.objects.filter(Q(topic__name__icontains=q)|
                              Q(name__icontains=q)|
                              Q(description__icontains=q)|
                              Q(host__username__icontains=q)
                              )
    topics=Topic.objects.all()
    rooms_count=rooms.count()
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q))  #.order_by("-created")

    context={"rooms":rooms,'topics':topics,'rooms_count':rooms_count,'room_messages':room_messages}
    return  render(request,'base/home.html',context)

def room(request,pk):
    room=Room.objects.get(id=pk)
    #all messages of the message  child  class of Room parent  model
    room_messages=room.message_set.all()  #.order_by('-created') # meny to one relation  ship
    participants=room.participants.all() # meny to meny relationship

    if request.method=='POST':
        message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        #participants user join the participants  list
        room.participants.add(request.user)
        return redirect('room',pk=room.id)

    context={'room':room,'room_messages':room_messages,"participants":participants}

    return render(request,'base/room.html',context)

@login_required(login_url="login")
def createRoom(request):
    form=RoomForm()
    if request.method=="POST":
        form=RoomForm(request.POST)
        if form.is_valid():
            room=form.save(commit=False)
            room.host=request.user
            room.save()
            return redirect("/")

    context={"form":form}
    return render(request,'base/room_form.html',context)

@login_required(login_url="login")
def updateRoom(request,pk):
    room=Room.objects.get(id=pk)
    form=RoomForm(instance=room)

    if  request.user != room.host:
        return HttpResponse("<p>you are not correct person </p>")
    if request.method=="POST":
        form=RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")

    context={
        'form':form
    }
    return render(request,'base/room_form.html',context)

@login_required(login_url="login")
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)
    if request.method=='POST':
        room.delete()
        return redirect('/')
    return render(request,'base/delete_room.html',{'obj':room})


@login_required(login_url="login")
def deleteMessage(request,pk):
    message=Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("you ar not allowed her !! ")
    
    if request.method=='POST':
        message.delete()
        return redirect('/')
    return render(request,'base/delete_room.html',{'obj':message})


def login_page(request):
    page='login'
    if request.user.is_authenticated:
        return redirect("/")
    if request.method=='POST':
        username=request.POST.get('username').lower()
        password=request.POST.get('password')
        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request,"User does not exist")
        
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('/')
        else:
            messages.error(request,'Username or password does not exists')
    context={'page':page}
    return render(request,'base/login_register.html',context)

def logout_user(request):
    logout(request)
    return redirect("/")

def register_user(request):
    form=UserCreationForm()
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('/')


    context={'form':form}
    return render(request,'base/login_register.html',context)


def userprofile(request,pk):
    user=User.objects.get(id=pk)
    rooms=user.room_set.all()
    rooms_messages=user.message_set.all()
    topic=Topic.objects.all()
    context={'user':user,'rooms':rooms,'room_messages':rooms_messages,'topic':topic}
    return render(request,'base/profile.html',context)