from math import ceil
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, post_delete


class ChessPiece(models.Model):
	type = models.ForeignKey('ChessPieceType', on_delete=models.CASCADE, verbose_name='typ', related_name='+')
	side = models.ForeignKey('chessgames.Side', on_delete=models.CASCADE, verbose_name='strona')
	position = models.OneToOneField('ChessField', on_delete=models.CASCADE, verbose_name='położenie na szachownicy', blank=True, null=True)
	initial_position = models.OneToOneField('ChessField', related_name='initially_occupied_by', on_delete=models.CASCADE, verbose_name='początkowe położenie', blank=True, null=True)
	
	def is_on_board(self):
		return self.position is not None
		
	def previous_position(self):
		moves = self.chesspiecemove_set.all().order_by('-time')
		if moves.count() >= 2:
			return moves[1].destination
		else:
			return self.initial_position
		
	def get_valid_moves(self):
		pass
				
	def is_move_valid(self, destination):
		pass
		
	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created:
			instance.initial_position = instance.position
			instance.save()
	
	def __str__(self):
		return '{} na polu {} w grze nr {}'.format(self.type.name, self.position.id_on_board(), self.side.chessgame.id)
		
	class Meta:
		verbose_name = "figura"
		verbose_name_plural = "figury"
		
		
post_save.connect(ChessPiece.post_save, ChessPiece)

		
class ChessPieceType(models.Model):
	id = models.SlugField(primary_key=True, max_length=20)
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
			
	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created:
			if hasattr(instance.destination, 'chesspiece'):
				instance.captured_piece = instance.destination.chesspiece
				instance.destination.chesspiece.position = None
			instance.moved_piece.position = instance.destination
			instance.save()
			if instance.captured_piece:
				instance.captured_piece.save()
			instance.moved_piece.save()
			
	@staticmethod
	def post_delete(sender, instance, **kwargs):
		previous_positions = instance.moved_piece.chesspiecemove_set.all().order_by('-time')
		if previous_positions.count() > 0:
			previous_pos = previous_positions[0].destination
		else:
			previous_pos = instance.moved_piece.initial_position
		instance.moved_piece.position = previous_pos
		if instance.captured_piece:
			instance.captured_piece.position = instance.destination
		instance.moved_piece.save()
		if instance.captured_piece:
			instance.captured_piece.save()
		
	def __str__(self):
		return 'Ruch nr {}: {} na {}'.format(self.pk, self.moved_piece.type.name, self.destination.id_on_board())
		
	class Meta:
		verbose_name = "ruch figury"
		verbose_name_plural = "ruchy figur"

		
post_save.connect(ChessPieceMove.post_save, ChessPieceMove)
post_delete.connect(ChessPieceMove.post_delete, ChessPieceMove)


class ChessFieldManager(models.Manager):
	def get_queryset(self, *args, **kwargs):
		return super(ChessFieldManager, self).get_queryset().order_by("-chessgame", "pk")
	
	def get_by_id_on_board(self, chessgame, id_on_board):
		column = id_on_board % 8
		if column == 0:
			column = 8
		row = ceil(id_on_board / 8)
		print ('col {}, row {}, id {}'.format(column, row, id_on_board))
		return self.get(chessgame=chessgame, row=row, column=column)
		
	
class ChessField(models.Model):
	row = models.PositiveSmallIntegerField()
	column = models.PositiveSmallIntegerField()
	chessgame = models.ForeignKey('chessgames.ChessGame', on_delete=models.CASCADE, verbose_name='szachownica')
	
	objects = ChessFieldManager()
	
	def id_on_board(self):
		return 8*(self.row-1) + self.column
	
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
