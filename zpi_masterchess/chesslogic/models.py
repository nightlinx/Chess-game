from django.db import models


class ChessPiece(models.Model):
	type = models.ForeignKey('ChessPieceType', on_delete=models.CASCADE, verbose_name='typ', related_name='+')
	side = models.ForeignKey('chessgames.Side', on_delete=models.CASCADE, verbose_name='strona', related_name='chesspieces')
	
	def is_on_board(self):
		pass
		
	def position(self):
		pass
		
	def previous_position(self):
		pass
		
	def get_valid_moves(self):
		pass
		
	def is_move_valid(self, destination):
		pass

	def clean(self):
		pass
	
	def __str__(self):
		return '{} - {} - {}'.format(self.type.name, self.participation.player.username, self.participation.chessgame)
		
	class Meta:
		verbose_name = "figura"
		verbose_name_plural = "figury"
		
		
class ChessPieceType(models.Model):
	name = models.CharField('nazwa', max_length=20)
	value = models.PositiveSmallIntegerField('wartość punktowa', default=1)
	
	def clean(self):
		pass
	
	def __str__(self):
		return '{} (wartość: {})'.format(self.name, self.value)
		
	class Meta:
		verbose_name = "rodzaj figury"
		verbose_name_plural = "rodzaje figur"
		

class ChessPieceMove(models.Model):
	# TODO: ChessPiecePositionField
	moved_piece = models.ForeignKey(ChessPiece, on_delete=models.CASCADE, verbose_name='poruszona figura', related_name='moves')
	captured_piece = models.ForeignKey(ChessPiece, on_delete=models.CASCADE, verbose_name='zbita figura', related_name='captured_by', null=True, blank=True)
	time = models.DateTimeField('kiedy wykonany', auto_now_add=True)
	
	def chessgame(self):
		pass
	
	def side(self):
		pass
	
	def chessplayer(self):
		pass
		
	def clean(self):
		pass
	
	def __str__(self):
		return '{}'.format(self.pk)
		
	class Meta:
		verbose_name = "ruch figury"
		verbose_name_plural = "ruchy figur"
