from django.db import models


class ChessGameManager(models.Manager):
	def get_queryset(self, *args, **kwargs):
		return super(ChessGameManager, self).get_queryset().order_by("-pk")

		
class ChessGame(models.Model):
	start_date = models.DateTimeField("czas rozpoczęcia", null=True, blank=True)
	end_date = models.DateTimeField("czas zakończenia", null=True, blank=True)
	
	objects = ChessGameManager()
	
	def is_awaiting_opponent(self):
		pass
		
	def is_finished(self):
		pass
		
	def is_tied(self):
		pass
		
	def chesspieces(self):
		pass
		
	def participants(self):
		pass
		
	def initialize_game(self):
		pass
		
	def test_end_conditions(self):
		pass

	def clean(self):
		pass
	
	def __str__(self):
		return 'Gra nr {}'.format(self.pk)
		
	class Meta:
		verbose_name = "gra"
		verbose_name_plural = "gry"
		

class Side(models.Model):
	player = models.ForeignKey('chessplayers.Player', on_delete=models.CASCADE, verbose_name='gracz', related_name='participations')
	chessgame = models.ForeignKey(ChessGame, on_delete=models.CASCADE, verbose_name='gra', related_name='participations')
	difficulty_level = models.ForeignKey('DifficultyLevel', on_delete=models.PROTECT, verbose_name='poziom trudności', related_name='+')
	WHITE = 1
	BLACK = 2
	COLOR_CHOICES = (
		(WHITE, 'Białe'),
		(BLACK, 'Czarne'),
	)
	color = models.PositiveSmallIntegerField('kolor', choices=COLOR_CHOICES, default=WHITE)
	WIN = 1
	LOSS = -1
	TIE = 0
	RESULT_CHOICES = (
		(WIN, 'Zwyciestwo'),
		(LOSS, 'Porażka'),
		(TIE, 'Remis'),
	)
	result = models.SmallIntegerField('rezultat', choices=RESULT_CHOICES, null=True, blank=True)
	
	def points(self):
		pass
		
	def cancel_last_move(self):
		pass
	
	def clean(self):
		pass
	
	def __str__(self):
		return 'Udział {} w grze nr {}'.format(self.player, self.chessgame.pk)
		
	class Meta:
		verbose_name = "strona"
		verbose_name_plural = "strona"

		
class DifficultyLevel(models.Model):
	name = models.CharField('nazwa', max_length=40)
	level = models.PositiveSmallIntegerField('poziom', help_text='Numeryczna wartość poziomu trudności. Im wyższa tym trudniej.', default=50)
	can_cancel_last_move = models.BooleanField(default=False)
	can_see_valid_moves = models.BooleanField(default=False)
	can_see_threats = models.BooleanField(default=False)
	can_see_hints = models.BooleanField(default=False)

	def clean(self):
		pass
	
	def __str__(self):
		return '{} ({})'.format(self.name, self.level)
		
	class Meta:
		verbose_name = "poziom trudności"
		verbose_name_plural = "poziomy trudności"
	