from django.db import models
from django.core.exceptions import ValidationError


class ChessPiece(models.Model):
	type = models.ForeignKey('ChessPieceType', on_delete=models.CASCADE, verbose_name='typ', related_name='+')
	side = models.ForeignKey('chessgames.Side', on_delete=models.CASCADE, verbose_name='strona')
	position = models.ForeignKey('ChessField', on_delete=models.CASCADE, verbose_name='położenie na szachownicy', blank=True, null=True)
	
	def is_on_board(self):
		return self.position is not None
		
	def previous_position(self):
		moves = self.chesspiecemove_set.all().order_by('-time')
		if moves.count() >= 2:
			return moves[1]
		else:
			return None
		
	def get_valid_moves(self):
		pass
		
	def is_move_valid(self, destination):
		pass
	
	def __str__(self):
		return '{} - {} - {}'.format(self.type.name, self.side.get_color_display(), self.side.chessgame)
		
	class Meta:
		verbose_name = "figura"
		verbose_name_plural = "figury"
		
		
class ChessPieceType(models.Model):
	name = models.CharField('nazwa', max_length=20)
	value = models.PositiveSmallIntegerField('wartość punktowa', default=1)
	
	def __str__(self):
		return '{} (wartość: {})'.format(self.name, self.value)
		
	class Meta:
		verbose_name = "rodzaj figury"
		verbose_name_plural = "rodzaje figur"


class ChessPieceMove(models.Model):
	destination = models.ForeignKey('ChessField', on_delete=models.CASCADE, verbose_name='docelowe pole')
	moved_piece = models.ForeignKey(ChessPiece, on_delete=models.CASCADE, verbose_name='poruszona figura')
	captured_piece = models.ForeignKey(ChessPiece, on_delete=models.CASCADE, verbose_name='zbita figura', related_name='captured_by', null=True, blank=True)
	time = models.DateTimeField('kiedy wykonany', auto_now_add=True)
	
	def chessgame(self):
		return self.moved_piece.side.chessgame
	
	def side(self):
		return self.moved_piece.side
	
	def chessplayer(self):
		return self.moved_piece.side.player
		
	def clean(self):
		if self.captured_piece:
			if self.moved_piece.side == self.captured_piece.side:
				raise ValidationError('Nie można zbić swojej figury', code='side-mismatch')
			if self.captured_piece.is_on_board():
				raise ValidationError('Figura oznaczona jako zbita nadal znajduje się na planszy.', code='piece-not-captured')
			if self.destination.chessgame != self.captured_piece.side.chessgame:
				raise ValidationError('Nie można zbić figury z innej szachownicy.', code='chessgame-mismatch')
		if self.destination.chessgame != self.moved_piece.side.chessgame:
			raise ValidationError('Figura nie może znaleźć się na innej szachownicy.', code='chessgame-mismatch')
	
	def __str__(self):
		return '{} - {}'.format(self.pk, self.moved_piece)
		
	class Meta:
		verbose_name = "ruch figury"
		verbose_name_plural = "ruchy figur"

		
class ChessField(models.Model):
	row = models.PositiveSmallIntegerField()
	column = models.PositiveSmallIntegerField()
	chessgame = models.ForeignKey('chessgames.ChessGame', on_delete=models.CASCADE, verbose_name='szachownica')
	
	def id_on_board(self):
		return 8*(self.row-1) + self.column
		
	def chesspiece(self):
		return self.chesspiece_set.all().first()
	
	def is_empty(self):
		return self.chesspiece is None
	
	def __str__(self):
		return 'Pole {} szachownicy {}'.format(self.id_on_board(), self.chessgame.id)
		
	class Meta:
		verbose_name = "pole szachownicy"
		verbose_name_plural = "pola szachownic"
		unique_together = (
			('row', 'column', 'chessgame')
		)
