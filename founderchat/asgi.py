"""
ASGI config for founderchat project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
import logging
from typing import Any, Dict

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Configure Django settings before importing routing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'founderchat.settings')
django.setup()

logger = logging.getLogger(__name__)

# Import routing configurations
from video_call.routing import websocket_urlpatterns as video_call_websocket_urlpatterns
from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns

# Combine websocket URL patterns
all_websocket_urlpatterns = video_call_websocket_urlpatterns + chat_websocket_urlpatterns

# Create the base application
django_asgi_app = get_asgi_application()

class LoggingASGIApplication:
    """
    ASGI application wrapper that logs errors
    """
    def __init__(self, application):
        self.application = application

    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        try:
            await self.application(scope, receive, send)
        except Exception as e:
            logger.error(f"Error in ASGI application: {str(e)}", exc_info=True)
            raise

# Define the ASGI application with proper routing
application = LoggingASGIApplication(
    ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(all_websocket_urlpatterns)
            )
        ),
    })
)
