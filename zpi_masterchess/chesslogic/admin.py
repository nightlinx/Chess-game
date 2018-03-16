from django.contrib import admin
from .models import ChessPiece, ChessPieceType, ChessPieceMove, ChessField

admin.site.register(ChessPiece)
admin.site.register(ChessPieceType)
admin.site.register(ChessPieceMove)
admin.site.register(ChessField)
