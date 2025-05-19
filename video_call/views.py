from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def video_call(request, room_name):
    return render(request, 'video_call/video_call.html', {
        'room_name': room_name,
        'username': request.user.username
    })
