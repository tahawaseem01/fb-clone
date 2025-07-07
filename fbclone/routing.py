from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import accounts.routing  # ✅ Use your actual app name here

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            accounts.routing.websocket_urlpatterns
        )
    ),
})
