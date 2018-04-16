from rest_framework import serializers
from .models import ChessGame, Side, DifficultyLevel


class ChessGameSerializer(serializers.ModelSerializer):
	class Meta:
		model = ChessGame
		fields = ('id', 'start_date', 'end_date', 'side_set', 'chessfield_set')


class SideSerializer(serializers.ModelSerializer):
	class Meta:
		model = Side
		fields = ('id', 'player', 'chessgame', 'difficulty_level', 'color', 'result', 'chesspiece_set', 'chesspiecemove_set', )
		

class DifficultyLevelSerializer(serializers.ModelSerializer):
	class Meta:
		model = DifficultyLevel
		fields = ('id', 'name', 'level', 'can_cancel_last_move', 'can_see_valid_moves', 'can_see_threats', 'can_see_hints')
