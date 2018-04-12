from rest_framework import routers
from .viewsets import ChessGameViewSet, SideViewSet, DifficultyLevelViewSet


router = routers.SimpleRouter()
router.register(r'chessgame', ChessGameViewSet)
router.register(r'side', SideViewSet)
router.register(r'difficultylevel', DifficultyLevelViewSet)

urlpatterns = router.urls
