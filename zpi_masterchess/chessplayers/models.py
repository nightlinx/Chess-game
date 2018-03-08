from django.contrib.auth.models import User
from django.db import models


class PlayerManager(models.Manager):
	def get_queryset(self, *args, **kwargs):
		return super(PlayerManager, self).get_queryset().order_by("user__username")


class Player(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="połączone konto")
	
	objects = PlayerManager()
	
	def username(self):
		return self.user.username
		
	def email(self):
		return self.user.email
		
	def chessgames(self):
		pass
		
	def current_chessgame(self):
		pass
		
	def clean(self):
		pass
		
	def __str__(self):
		return '{} ({})'.format(self.user.username, self.pk)
		
	class Meta:
		verbose_name = "gracz"
		verbose_name_plural = "gracze"
