from rest_framework import routers
from .viewsets import PlayerViewSet


router = routers.SimpleRouter()
router.register(r'player', PlayerViewSet)

urlpatterns = router.urls
