from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from chesslogic.models import ChessField

class ChessGameManager(models.Manager):
	def get_queryset(self, *args, **kwargs):
		return super(ChessGameManager, self).get_queryset().order_by("-pk")
		
	def games_awaiting_oppontent(self, *args, **kwargs):
		return self.get_queryset().filter(is_awaiting_opponent=True)
		
	def finished_games(self, *args, **kwargs):
		return self.get_queryset().filter(is_finished=True)
		
	def currently_played_games(self, *args, **kwargs):
		return self.get_queryset().filter(is_awaiting_opponent=False, is_finished=False)

		
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
		
	def initialize_game(self):
		for row in range(1, 9):
			for column in range(1, 9):
				print("tworzę chessfield")
				ChessField.objects.create(row=row, column=column, chessgame=self)
		
	def test_end_conditions(self):
		pass

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
			instance.save()
			instance.initialize_game()
	
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
		
	def moves(self):
		all_moves = []
		for piece in self.chesspiece_set.all():
			for move in piece.chesspiecemove_set.all():
				all_moves.append(move)
		return all_moves
		
	def opposite_side(self):
		sides = self.chessgame.side_set.all()
		if (sides.count() == 1):
			return None
		else:
			return sides.filter(pk__ne=self.pk)[0]
		
	def cancel_last_move(self):
		pass
	
	def __str__(self):
		return 'Strona {} w grze nr {}'.format(self.color, self.chessgame.pk)
		
	class Meta:
		verbose_name = "strona"
		verbose_name_plural = "strony"
		unique_together = (
			('player', 'chessgame'),
			('color', 'chessgame')
		)

		
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
	