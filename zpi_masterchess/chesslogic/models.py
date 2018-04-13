import chess
from math import ceil
from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, post_delete


class ChessPiece(models.Model):
	type = models.ForeignKey('ChessPieceType', on_delete=models.CASCADE, verbose_name='typ', related_name='+')
	side = models.ForeignKey('chessgames.Side', on_delete=models.CASCADE, verbose_name='strona')
	position = models.OneToOneField('ChessField', on_delete=models.CASCADE, verbose_name='położenie na szachownicy')
		
	def legal_moves(self):
		all_legal_moves = self.side.chessgame.lib_legal_moves()
		return [move.to_square for move in all_legal_moves if move.from_square == self.position.lib_instance()]
				
	def is_move_legal(self, to_field):
		return to_field in self.legal_moves()
	
	def __str__(self):
		return '{} na polu {}'.format(self.type.name, self.position)
		
	class Meta:
		verbose_name = "figura"
		verbose_name_plural = "figury"

		
class ChessPieceType(models.Model):
	id = models.PositiveSmallIntegerField(primary_key=True)
	name = models.CharField('nazwa', max_length=20)
	value = models.PositiveSmallIntegerField('wartość punktowa', default=1)
	
	def __str__(self):
		return self.name
		
	def lib_instance(self):
		return id
		
	def type_and_color(self, color):
		'''
			1 : White Pawn			7 : Black Pawn
			2 : White Knight		8 : Black Knight	
			3 : White Bishop		9 : Black Bishop
			4 : White Rook			10 : Black Rook
			5 : White Queen			11 : Black Queen
			6 : White King			12 : Black King
		'''
		multiplier = 0 if color == apps.get_model('chessgames', 'Side').WHITE else 1
		return self.id + multiplier * 6
		
	class Meta:
		verbose_name = "rodzaj figury"
		verbose_name_plural = "rodzaje figur"


class ChessPieceMove(models.Model):
	from_field = models.ForeignKey('ChessField', on_delete=models.CASCADE, verbose_name='skąd', related_name='+')
	to_field = models.ForeignKey('ChessField', on_delete=models.CASCADE, verbose_name='dokąd', related_name='+')
	promotion_type = models.ForeignKey('ChessPieceType', on_delete=models.CASCADE, verbose_name='typ figury promocji', help_text='Jeśli ruch powoduje promocję piona, zostanie on zamieniony na figurę tego typu.', blank=True, null=True)
	time = models.DateTimeField('kiedy wykonany', auto_now_add=True)
	side = models.ForeignKey('chessgames.Side', on_delete=models.CASCADE, verbose_name='strona wykonująca ruch')
	
	def chessgame(self):
		return self.side.chessgame
	
	def chessplayer(self):
		return self.side.player
		
	def lib_instance(self):
		if self.promotion_type:
			promotion = self.promotion_type.lib_instance()
		else:
			promotion = None
		return chess.Move(self.from_field.lib_instance(), self.to_field.lib_instance(), promotion)
		
	def clean(self):
		if self.lib_instance() not in self.chessgame().lib_legal_moves():
			raise ValidationError('Niedozwolony ruch', 'illegal-move')
		if self.from_field.chessgame != self.to_field.chessgame:
			raise ValidationError('Nie można przenosić figur między szachownicami.', code='chessgame-mismatch')
		if self.side.chessgame != self.to_field.chessgame:
			raise ValidationError('Strona wykonująca ruch nie bierze udziału w tej grze', code='side-mismatch')
			
	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created:
			instance.chessgame().lib_synch()
			instance.chessgame().save()
			
	@staticmethod
	def post_delete(sender, instance, **kwargs):
		instance.chessgame().lib_synch()
		instance.chessgame().save()
		
	def __str__(self):
		return '{} na {} w grze {}'.format(self.from_field.name().upper(), self.to_field.name().upper(), self.chessgame().id)
		
	class Meta:
		verbose_name = "ruch figury"
		verbose_name_plural = "ruchy figur"

		
post_save.connect(ChessPieceMove.post_save, ChessPieceMove)
post_delete.connect(ChessPieceMove.post_delete, ChessPieceMove)

	
class ChessField(models.Model):
	field_id = models.PositiveSmallIntegerField('id na szachownicy')
	chessgame = models.ForeignKey('chessgames.ChessGame', on_delete=models.CASCADE, verbose_name='szachownica')
	
	def is_empty(self):
		return self.chesspiece is None
		
	def file(self):
		return chess.square_file(self.field_id)
	
	def rank(self):
		return chess.square_rank(self.field_id)
		
	def file_name(self):
		return chess.FILE_NAMES[chess.square_file(self.field_id)]
		
	def rank_name(self):
		return chess.RANK_NAMES[chess.square_rank(self.field_id)]
	
	def name(self):
		return chess.SQUARE_NAMES[self.field_id]
	
	def lib_instance(self):
		return self.field_id
	
	def __str__(self):
		return '{} ({}) na szachownicy {}'.format(self.name().upper(), self.field_id, self.chessgame.pk)
		
	class Meta:
		verbose_name = "pole szachownicy"
		verbose_name_plural = "pola szachownic"
		unique_together = (
			('field_id', 'chessgame')
		)
