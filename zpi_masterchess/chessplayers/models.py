from django.contrib.auth.models import User
from django.db import models


class PlayerManager(models.Manager):
	def get_queryset(self, *args, **kwargs):
		return super(PlayerManager, self).get_queryset().order_by("user__username")
		
	def currently_playing(self, *args, **kwargs):
		return self.get_queryset().filter(current_chessgame__isnull=False)


class Player(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="połączone konto")
	
	objects = PlayerManager()
	
	def username(self):
		return self.user.username
		
	def email(self):
		return self.user.email
		
	def chessgames(self):
		all_games = []
		for side in self.side_set.all():
			all_games.append(side.chessgame)
		return all_games
		
	def current_chessgame(self):
		sides = self.side_set.all().filter(chessgame__end_date__isnull=True).order_by('-chessgame__start_date')
		if sides.count() > 0:
			return sides.first().chessgame
		else:
			return None
		
	def __str__(self):
		return '{} ({})'.format(self.user.username, self.pk)
		
	class Meta:
		verbose_name = "gracz"
		verbose_name_plural = "gracze"
