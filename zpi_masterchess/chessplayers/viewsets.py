from collections import OrderedDict
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Player
from .serializers import PlayerSerializer


class PlayerViewSet(viewsets.ModelViewSet):
	queryset = Player.objects.all()
	serializer_class = PlayerSerializer
	
	def retrieve(self, request, pk=None):
		player = self.get_object()
		current_chessgame = player.current_chessgame()
		return Response(OrderedDict([
			('player_id', player.pk),
			('name', player.username()),
			('current_chessgame', player.current_chessgame().pk if current_chessgame else None),
			('all_chessgames', [chessgame.pk for chessgame in player.chessgames()]),
		]))
