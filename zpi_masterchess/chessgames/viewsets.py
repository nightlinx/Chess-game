from collections import OrderedDict
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ChessGame, Side, DifficultyLevel
from chesslogic.models import ChessField, ChessPieceMove, ChessPieceType
from .serializers import ChessGameSerializer, SideSerializer, DifficultyLevelSerializer
from chesslogic.serializers import ChessPieceMoveSerializer
from chessplayers.models import Player


class ChessGameViewSet(viewsets.ModelViewSet):
	queryset = ChessGame.objects.all()
	serializer_class = ChessGameSerializer
	

	def retrieve(self, request, pk=None):
		chessgame = self.get_object()
		id = chessgame.pk
		turn = 'white' if chessgame.turn().color == Side.WHITE else 'black'
		chesspieces = [
			OrderedDict([
				('type_id', chesspiece.type.type_and_color(chesspiece.side.color)),
				('chessfield_id', chesspiece.position.field_id),
				('legal_moves', chesspiece.legal_moves()),
			])
			for chesspiece in chessgame.chesspieces()
		]
		players = [
			OrderedDict([
				('player_id', side.player.user.pk),
				('name', side.player.username()),
				('color', 'white' if side.color == Side.WHITE else 'black'),
				('points', side.points()),
				('moves', [
					OrderedDict([
						('move_id', move.pk),
						('from_field', move.from_field.field_id),
						('to_field', move.to_field.field_id),
						('promotion_type', move.promotion_type),
						('time', move.time),
					])
					for move in side.chesspiecemove_set.all()
				]),
			])
			for side in chessgame.side_set.all()
		]
		return Response(OrderedDict([
			('chessgame_id', id),
			('turn', turn),
			('chesspieces', chesspieces),
			('players', players),
		]))
		
	@action(detail=False)
	def get_games_awaiting_opponent(self, request):
		games_awaiting_oppontent = ChessGame.objects.games_awaiting_oppontent()
		serializer = self.get_serializer(games_awaiting_oppontent, many=True)
		return Response(serializer.data)

	@action(methods=['get'], detail=True)
	def get_legal_moves(self, request, pk=None):
		chessgame = self.get_object()
		try:
			field_id = int(request.query_params.get('field_id'))
			chessfield = ChessField.objects.get(chessgame=chessgame, field_id=field_id)
		except (ChessField.DoesNotExist, TypeError):
			return Response({'error': 'Incorrect field_id'}, status=status.HTTP_400_BAD_REQUEST)
		legal_moves = chessfield.chesspiece.legal_moves() if hasattr(chessfield, 'chesspiece') else []
		return Response(OrderedDict([
			('chessfield_id', chessfield.field_id),
			('legal_moves', legal_moves),
		]))
		
	@action(methods=['post'], detail=True)
	def make_move(self, request, pk=None):
		chessgame = self.get_object()
		from_field_id = request.data.get("from_field")
		to_field_id = request.data.get("to_field")
		promotion_type_id = request.data.get("promotion_type")
		
		try:
			from_field = ChessField.objects.get(chessgame=chessgame, field_id=from_field_id)
			to_field = ChessField.objects.get(chessgame=chessgame, field_id=to_field_id)
			if promotion_type_id:
				promotion_type = ChessPieceType.objects.get(id=promotion_type_id)
			else:
				promotion_type = None
		except (ChessField.DoesNotExist, ChessPieceType.DoesNotExist, TypeError) as e:
			return Response({'status': str(e)}, status=status.HTTP_400_BAD_REQUEST)
			
		chesspiecemove = ChessPieceMove(
			side=chessgame.turn(), from_field=from_field, to_field=to_field, promotion_type=promotion_type)
			
		try:
			chesspiecemove.full_clean()
		except:
			return Response({'status': 'Invalid move'})
		
		chesspiecemove.save()
		return Response({'status': 'Success'})

		
class SideViewSet(viewsets.ModelViewSet):
	queryset = Side.objects.all()
	serializer_class = SideSerializer


class DifficultyLevelViewSet(viewsets.ModelViewSet):
	queryset = DifficultyLevel.objects.all()
	serializer_class = DifficultyLevelSerializer
