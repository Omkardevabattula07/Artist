import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import Artist_app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Artist.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            Artist_app.routing.websocket_urlpatterns
        )
    ),
})
