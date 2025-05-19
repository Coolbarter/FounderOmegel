from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        'accounts': {
            'register': reverse('register', request=request, format=format),
            'user_detail': reverse('user-detail', request=request, format=format),
            'change_password': reverse('change-password', request=request, format=format),
        },
        'profiles': {
            'list': reverse('profile-list', request=request, format=format),
            'create': reverse('profile-create', request=request, format=format),
            'detail': reverse('profile-detail', request=request, format=format),
        },
        'matchmaking': {
            'list': reverse('match-list', request=request, format=format),
            'create': reverse('match-create', request=request, format=format),
            'recommendations': reverse('match-recommendations', request=request, format=format),
        },
        'chat': {
            'rooms': reverse('chat-room-create', request=request, format=format),
            'messages': reverse('message-create', request=request, format=format),
        },
        'authentication': {
            'token_obtain': reverse('token_obtain_pair', request=request, format=format),
            'token_refresh': reverse('token_refresh', request=request, format=format),
        }
    }) 