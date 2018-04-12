from rest_framework import viewsets
from .models import ChessGame, Side, DifficultyLevel
from .serializers import ChessGameSerializer, SideSerializer, DifficultyLevelSerializer


class ChessGameViewSet(viewsets.ModelViewSet):
    queryset = ChessGame.objects.all()
    serializer_class = ChessGameSerializer
	
	
class SideViewSet(viewsets.ModelViewSet):
	queryset = Side.objects.all()
	serializer_class = SideSerializer


class DifficultyLevelViewSet(viewsets.ModelViewSet):
	queryset = DifficultyLevel.objects.all()
	serializer_class = DifficultyLevelSerializer
