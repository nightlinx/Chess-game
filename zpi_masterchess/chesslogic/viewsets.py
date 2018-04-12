from rest_framework import viewsets
from .models import ChessPiece, ChessPieceType, ChessPieceMove, ChessField
from .serializers import ChessPieceSerializer, ChessPieceTypeSerializer, ChessPieceMoveSerializer, ChessFieldSerializer


class ChessPieceViewSet(viewsets.ModelViewSet):
    queryset = ChessPiece.objects.all()
    serializer_class = ChessPieceSerializer


class ChessPieceTypeViewSet(viewsets.ModelViewSet):
    queryset = ChessPieceType.objects.all()
    serializer_class = ChessPieceTypeSerializer


class ChessPieceMoveViewSet(viewsets.ModelViewSet):
    queryset = ChessPieceMove.objects.all()
    serializer_class = ChessPieceMoveSerializer


class ChessFieldViewSet(viewsets.ModelViewSet):
    queryset = ChessField.objects.all()
    serializer_class = ChessFieldSerializer
	