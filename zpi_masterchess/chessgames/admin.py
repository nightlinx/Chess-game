from django.contrib import admin
from .models import ChessGame, Side, DifficultyLevel

admin.site.register(ChessGame)
admin.site.register(Side)
admin.site.register(DifficultyLevel)
