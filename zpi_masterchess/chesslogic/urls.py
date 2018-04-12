from rest_framework import routers
from .viewsets import ChessPieceViewSet, ChessPieceTypeViewSet, ChessPieceMoveViewSet, ChessFieldViewSet


router = routers.SimpleRouter()
router.register(r'chesspiece', ChessPieceViewSet)
router.register(r'chesspiecetype', ChessPieceTypeViewSet)
router.register(r'chesspiecemove', ChessPieceMoveViewSet)
router.register(r'chessfield', ChessFieldViewSet)

urlpatterns = router.urls
