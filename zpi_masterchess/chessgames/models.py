import chess
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from chesslogic.models import ChessField, ChessPiece, ChessPieceType, ChessPieceMove

class ChessGameManager(models.Manager):
	def get_queryset(self, *args, **kwargs):
		return super(ChessGameManager, self).get_queryset().order_by("-pk")
		
	def games_awaiting_oppontent(self, *args, **kwargs):
		return self.get_queryset().filter(start_date__isnull=True)
		
	def finished_games(self, *args, **kwargs):
		return self.get_queryset().filter(end_date__isnull=False)
		
	def currently_played_games(self, *args, **kwargs):
		return self.get_queryset().filter(start_date__isnull=False, end_date__isnull=False)

		
class ChessGame(models.Model):
	start_date = models.DateTimeField("czas rozpoczęcia", null=True, blank=True)
	end_date = models.DateTimeField("czas zakończenia", null=True, blank=True)
	
	objects = ChessGameManager()
	
	def is_awaiting_opponent(self):
		return self.start_date is None
		
	def is_finished(self):
		return self.end_date is not None 
		
	def is_tied(self):
		for side in self.side_set.all():
			if side.result == Side.TIE:
				return true
		return false
		
	def turn(self):
		if self.side_set.count() != 2:
			return None
		else:
			moves = self.moves().order_by('-time')
			if moves.count() == 0 or moves[0].side == self.black_side():
				return self.white_side()
			else:
				return self.black_side()
		
	def chesspieces(self):
		all_pieces = []
		for side in self.side_set.all():
			for piece in side.chesspiece_set.all():
				all_pieces.append(piece)
		return all_pieces
		
	def participants(self):
		all_participants = []
		for side in self.side_set.all():
			all_participants.append(side.player)
		return all_participants
		
	def black_side(self):
		black = self.side_set.all().filter(color=Side.BLACK)
		if black.count() > 0:
			return black[0]
		else:
			return None
			
	def white_side(self):
		white = self.side_set.all().filter(color=Side.WHITE)
		if white.count() > 0:
			return white[0]
		else:
			return None
		
	def moves(self):
		return ChessPieceMove.objects.all().filter(side__chessgame__pk=self.pk).order_by('time')
		
	def init_board(self):
		for field_id in range(0, 64, 1):
			ChessField.objects.create(field_id=field_id, chessgame=self)

	def lib_instance(self):
		board = chess.Board()
		for move in self.moves():
			board.push(move.lib_instance())
		return board
		
	def lib_legal_moves(self):
		return self.lib_instance().legal_moves
		
	def lib_synch(self):
		board = self.lib_instance()
		for field in self.chessfield_set.all():
			if hasattr(field, 'chesspiece'):
				piece = field.chesspiece
			else:
				piece = None
			lib_piece = board.piece_at(field.lib_instance())
			
			if piece is None and lib_piece is not None:
				if lib_piece.color:
					side = self.white_side()
				else:
					side = self.black_side()
				if side:
					ChessPiece.objects.create(type=ChessPieceType.objects.get(id=lib_piece.piece_type), side=side, position=field)
			elif piece is not None and lib_piece is None:
				piece.delete()
			elif piece is not None and lib_piece is not None:
				piece.type = ChessPieceType.objects.get(id=lib_piece.piece_type)
				if lib_piece.color:
					piece.side = self.white_side()
				else:
					piece.side = self.black_side()
				piece.save()
		if board.is_game_over():
			self.end_date = timezone.now()
			if board.result() == '1-0':
				self.white_side().result = Side.WIN
				self.black_side().result = Side.LOSS
			elif board.result() == '0-1':
				self.white_side().result = Side.LOSS
				self.black_side().result = Side.WIN
			elif board.result() == '1/2-1/2':
				self.white_side().result = Side.TIE
				self.black_side().result = Side.TIE
			self.white_side().save()
			self.black_side().save()

	def clean(self):
		if self.side_set.all().count() > 2:
			raise ValidationError('W grze może brać udział tylko dwóch graczy', code='too-many-players')
		if self.end_date and self.start_date:
			if self.end_date < self.start_date:
				raise ValidationError('Czas rozpoczęcia gry nie może być późniejszy niż czas zakończenia.', code='invalid-time')
		if self.end_date and not self.start_date:
			raise ValidationError('Gra nie może się zakończyć zanim się nie zacznie.', code='invalid-time')
			
	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created:
			instance.init_board()
	
	def __str__(self):
		return 'Gra nr {}'.format(self.pk)
		
	class Meta:
		verbose_name = "gra"
		verbose_name_plural = "gry"

		
post_save.connect(ChessGame.post_save, ChessGame)


class Side(models.Model):
	player = models.ForeignKey('chessplayers.Player', on_delete=models.CASCADE, verbose_name='gracz')
	chessgame = models.ForeignKey(ChessGame, on_delete=models.CASCADE, verbose_name='gra')
	difficulty_level = models.ForeignKey('DifficultyLevel', on_delete=models.PROTECT, verbose_name='poziom trudności', related_name='+')
	WHITE = 1
	BLACK = 2
	COLOR_CHOICES = (
		(WHITE, 'Białe'),
		(BLACK, 'Czarne'),
	)
	color = models.PositiveSmallIntegerField('kolor', choices=COLOR_CHOICES, default=WHITE)
	WIN = 1
	TIE = 2
	LOSS = 3
	RESULT_CHOICES = (
		(WIN, 'Zwyciestwo'),
		(TIE, 'Remis'),
		(LOSS, 'Porażka'),
	)
	result = models.SmallIntegerField('rezultat', choices=RESULT_CHOICES, null=True, blank=True)
	
	def points(self):
		all_points = 0
		for piece in self.chesspiece_set.all():
			all_points += piece.type.value
		return all_points
		
	def opposite_side(self):
		sides = self.chessgame.side_set.all()
		if (sides.count() == 1):
			return None
		else:
			return sides.exclude(pk=self.pk)[0]
		
	def cancel_last_move(self):
		pass
		
	def claim_tie(self):
		pass
		
	def give_up(self):
		pass
		
	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created and instance.opposite_side():
			instance.chessgame.start_date = timezone.now()
			instance.chessgame.lib_synch()
			instance.chessgame.save()
	
	def __str__(self):
		return '{} ({}) w grze {}'.format(self.get_color_display(), self.player.username(), self.chessgame.pk)
		
	class Meta:
		verbose_name = "strona"
		verbose_name_plural = "strony"
		unique_together = (
			('player', 'chessgame'),
			('color', 'chessgame')
		)

		
post_save.connect(Side.post_save, Side)

		
class DifficultyLevel(models.Model):
	name = models.CharField('nazwa', max_length=40, unique=True)
	level = models.PositiveSmallIntegerField('poziom', help_text='Numeryczna wartość poziomu trudności. Im wyższa tym trudniej.', default=50)
	can_cancel_last_move = models.BooleanField(default=False)
	can_see_valid_moves = models.BooleanField(default=False)
	can_see_threats = models.BooleanField(default=False)
	can_see_hints = models.BooleanField(default=False)
	
	def __str__(self):
		return '{} ({})'.format(self.name, self.level)
		
	class Meta:
		verbose_name = "poziom trudności"
		verbose_name_plural = "poziomy trudności"
	