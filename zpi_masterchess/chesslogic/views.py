from django.shortcuts import render
from django.http import Http404
from chessgames.models import ChessGame


def chessboard_debug_view(request, pk):
	try:
		chessgame = ChessGame.objects.get(pk=pk)
	except ChessGame.DoesNotExist:
		raise Http404
		
	return render(request, 'debug/board.html', {
		'chessgame': chessgame
	})
