from rest_framework import serializers
from .models import ChessPiece, ChessPieceType, ChessPieceMove, ChessField


class ChessPieceSerializer(serializers.ModelSerializer):
	class Meta:
		model = ChessPiece
		fields = ('id', 'type', 'side', 'position')

		
class ChessPieceTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model = ChessPieceType
		fields = ('id', 'name', 'value')

		
class ChessPieceMoveSerializer(serializers.ModelSerializer):
	class Meta:
		model = ChessPieceMove
		fields = ('id', 'from_field', 'to_field', 'promotion_type', 'time', 'side')

		
class ChessFieldSerializer(serializers.ModelSerializer):
	class Meta:
		model = ChessField
		fields = ('field_id', 'chessgame')